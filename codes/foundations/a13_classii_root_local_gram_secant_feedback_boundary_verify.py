#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-094 A13 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import ast
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
RESULT_ID = "A13-CLASSII-ROOT-LOCAL-GRAM-SECANT-FEEDBACK-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
SLUG = "root-local-gram-secant-feedback-boundary"

PRIMARY = REPO / "codes/foundations/a13_classii_root_local_gram_secant_feedback_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_root_local_gram_secant_feedback_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-root-local-gram-secant-feedback-boundary-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-root-local-gram-secant-feedback-boundary-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_root_local_gram_secant_feedback_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-root-local-gram-secant-feedback-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-root-local-gram-secant-feedback-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-root-local-gram-secant-feedback-boundary/result.json"

AUTHORITY = {
    "r079": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r086": (
        CLAIM_DIR / "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-rational-translated-wick-payload-comparable-reduction/result.json",
    ),
    "r092": (
        CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json",
    ),
    "r093": (
        CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-augmented-perspective-gibbs-gap-information-boundary/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "AUDIT-2026-07-27-A13-R093-ROOT-FACTOR-SQUARE-ALLOCATION",
    "AUDIT-2026-07-27-A13-R093-BG-CRITICAL-ROW-SCOPE",
    "NG-2026-07-27-A13-ABSOLUTE-REVISIT-SECANT-SUM",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(192, 200))
EXPLORATION_VERDICTS = {
    "EXP-000192": "advanced",
    "EXP-000193": "advanced",
    "EXP-000194": "advanced",
    "EXP-000195": "failed",
    "EXP-000196": "advanced",
    "EXP-000197": "failed",
    "EXP-000198": "inconclusive",
    "EXP-000199": "advanced",
}

NOTE_TOKENS = (
    "R-094",
    "evidence-anchor: theorem-3.1-quadratic-gram-curvature",
    "{8\\over105}2^{-3j_0}",
    "evidence-anchor: theorem-4.1-centered-gram-secant",
    "3+2\\sqrt2",
    "X^{1/2}(1+Y)^{1/6}",
    "evidence-anchor: lemma-5.1-fresh-derivative-form",
    "evidence-anchor: theorem-5.2-value-heat-control-prefix",
    "{16\\over7}2^{-3j_0}",
    "evidence-anchor: theorem-6.1-exact-nonduplication-split",
    "\\mathcal P_{R,\\theta}^>",
    "T_G^>",
    "conditional mean debts",
    "evidence-anchor: section-7-bg-critical-row-audit",
    "evidence-anchor: section-8-revisit-sixth-moment-no-go",
    "2\\|\\phi\\|_{L^6(\\mathbb T^3)}^6p^{-2}",
    "Complete rootwise packet embedding",
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


def pdf_reachable_names(root: Any) -> set[str]:
    """Return deterministic PDF name tokens reachable from a resolved root."""

    names: set[str] = set()
    seen_containers: set[int] = set()

    def visit(node: Any) -> None:
        get_object = getattr(node, "get_object", None)
        if callable(get_object):
            resolved = get_object()
            if resolved is not node:
                visit(resolved)
                return

        if isinstance(node, dict):
            marker = id(node)
            if marker in seen_containers:
                return
            seen_containers.add(marker)
            for key, value in node.items():
                names.add(str(key))
                visit(value)
            return

        if isinstance(node, (list, tuple)):
            marker = id(node)
            if marker in seen_containers:
                return
            seen_containers.add(marker)
            for value in node:
                visit(value)
            return

        if isinstance(node, str) and node.startswith("/"):
            names.add(node)

    visit(root)
    return names


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def result_passes(record: dict[str, Any]) -> bool:
    if record.get("status") == "PASS":
        passed = record.get("assertions_passed", record.get("passed"))
        total = record.get("assertions_total", record.get("assertion_count"))
        if isinstance(passed, int) and isinstance(total, int):
            return total > 0 and passed == total
        return record.get("failed", 0) == 0
    verdict = str(record.get("verdict", ""))
    failures = record.get("failures", [])
    return "PASS" in verdict and not failures


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("actual")
    return None


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


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

    for label, script, result_path in (
        ("primary", PRIMARY, PRIMARY_RESULT),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT),
    ):
        result_path.unlink(missing_ok=True)
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
        )
        add(f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add(f"{label}_fresh_result", result_path.exists(), repo_path(result_path), "fresh atomic output exists")

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest_load", True, "valid JSON", "valid JSON")

    child_records: dict[str, dict[str, Any]] = {}
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        try:
            child_records[label] = load_json(path)
        except Exception as error:
            child_records[label] = {}
            add(f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add(f"{label}_result_load", True, "valid JSON", "valid JSON")
            add(f"{label}_result_pass", result_passes(child_records[label]), child_records[label].get("status"), "PASS with all assertions")
            add(f"{label}_claim_id", child_records[label].get("claim_id") == CLAIM, child_records[label].get("claim_id"), CLAIM)
            add(f"{label}_result_id", child_records[label].get("result_id") == RESULT_ID, child_records[label].get("result_id"), RESULT_ID)

    contract = manifest.get("run_contract", {})
    for label in ("primary", "independent"):
        record = child_records[label]
        expected_count = contract.get(f"{label}_assertions")
        add(f"{label}_count_contract", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add(
            f"{label}_rows_all_pass",
            len(record.get("assertions", [])) == record.get("assertions_total")
            and all(row.get("status") == "PASS" for row in record.get("assertions", [])),
            len(record.get("assertions", [])),
            record.get("assertions_total"),
        )

    expected_schemas = {
        "primary": "tect/a13-root-local-gram-secant-feedback-boundary-primary/1.0",
        "independent": "tect/a13-root-local-gram-secant-feedback-boundary-independent/1.0",
    }
    for label, schema in expected_schemas.items():
        add(f"{label}_schema", child_records[label].get("schema") == schema, child_records[label].get("schema"), schema)

    primary_derived = child_records.get("primary", {}).get("derived", {})
    add("quadratic_kernel_value", primary_derived.get("quadratic_kernel_constant") == "8/105", primary_derived.get("quadratic_kernel_constant"), "8/105")
    add("mixed_kernel_value", primary_derived.get("mixed_square_kernel_constant") == "4/45", primary_derived.get("mixed_square_kernel_constant"), "4/45")
    add("prefix_kernel_value", primary_derived.get("prefix_hilbert_schmidt_constant") == "16/7", primary_derived.get("prefix_hilbert_schmidt_constant"), "16/7")
    exponent_ledger = primary_derived.get("exponent_ledger", {})
    expected_slacks = {
        "sharp_a2_da": ("1/6", "6"),
        "sharp_a3_da": ("1/15", "15"),
        "centered_gram_mixed": ("1/3", "3"),
        "fresh_derivative": ("1/6", "6"),
    }
    for label, (slack, moment) in expected_slacks.items():
        row = exponent_ledger.get(label, {})
        add(f"exponent_{label}_slack", row.get("slack") == slack, row.get("slack"), slack)
        add(f"exponent_{label}_moment", row.get("moment") == moment, row.get("moment"), moment)

    # Independence and anti-shortcut gates.
    independent_imports = imported_modules(INDEPENDENT)
    forbidden_import_fragments = (
        "a13_classii_root_local_gram_secant_feedback_boundary",
        "runpy",
        "importlib",
    )
    for fragment in forbidden_import_fragments:
        hits = sorted(module for module in independent_imports if fragment in module)
        add(f"independent_forbidden_import_{fragment}", not hits, hits, [])
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independent_no_primary_result_read", "primary-root-local-gram-secant" not in independent_text, "primary result path token" in independent_text, False)
    add("independent_declares_nonimporting", child_records.get("independent", {}).get("independence", {}).get("imports_primary") is False, child_records.get("independent", {}).get("independence", {}).get("imports_primary"), False)

    # Pinned predecessor manifests and executed runs.
    authority_manifest = manifest.get("authority", {})
    for label, (manifest_path, result_path) in AUTHORITY.items():
        for kind, path in (("manifest", manifest_path), ("result", result_path)):
            add(f"authority_{label}_{kind}_exists", path.exists(), repo_path(path), "exists")
            expected_hash = authority_manifest.get(label, {}).get(kind, {}).get("sha256")
            actual_hash = digest(path) if path.exists() else None
            add(f"authority_{label}_{kind}_hash", actual_hash == expected_hash, actual_hash, expected_hash)
        try:
            authority_result = load_json(result_path)
        except Exception as error:
            add(f"authority_{label}_result_load", False, repr(error), "valid JSON")
        else:
            add(f"authority_{label}_result_pass", result_passes(authority_result), authority_result.get("status", authority_result.get("verdict")), "accepted PASS authority")

    # Source hashes and versions.
    source_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    manifest_sources = manifest.get("sources", {})
    for label, path in source_paths.items():
        entry = manifest_sources.get(label, {})
        add(f"source_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        add(f"source_{label}_hash", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))
        if label != "proof_note":
            add(f"source_{label}_version", entry.get("version") == source_version(path), entry.get("version"), source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS):
        add(f"note_token_{index:02d}", token in note_text, token in note_text, True)
    hangul_ranges = ((0x1100, 0x11FF), (0x3130, 0x318F), (0xA960, 0xA97F), (0xAC00, 0xD7AF), (0xD7B0, 0xD7FF))
    has_hangul = any(any(lower <= ord(character) <= upper for lower, upper in hangul_ranges) for character in note_text)
    add("note_english_scope", not has_hangul, has_hangul, False)

    # PDF structure and manifest facts. Visual inspection is a human/tool gate
    # recorded in the manifest and separately performed before release.
    try:
        reader = PdfReader(PDF)
        page_text_lengths = [len((page.extract_text() or "").strip()) for page in reader.pages]
        pdf_names = pdf_reachable_names(reader.trailer.get("/Root", {}))
        pdf_pages = len(reader.pages)
        pdf_forms = bool(reader.get_fields())
        pdf_encrypted = reader.is_encrypted
    except Exception as error:
        pdf_pages, pdf_forms, pdf_encrypted, page_text_lengths, pdf_names = 0, True, True, [], set()
        add("pdf_load", False, repr(error), "readable PDF")
    else:
        add("pdf_load", True, "readable PDF", "readable PDF")
    pdf_entry = manifest.get("proof_pdf", {})
    add("pdf_pages", pdf_pages == pdf_entry.get("pages") and pdf_pages >= 1, pdf_pages, pdf_entry.get("pages"))
    add("pdf_nonblank_pages", bool(page_text_lengths) and min(page_text_lengths) > 100, page_text_lengths, "each page >100 extracted characters")
    add("pdf_no_forms", not pdf_forms, pdf_forms, False)
    add("pdf_not_encrypted", not pdf_encrypted, pdf_encrypted, False)
    forbidden_pdf_names = sorted(pdf_names.intersection({"/JavaScript", "/JS"}))
    add("pdf_no_javascript", not forbidden_pdf_names, forbidden_pdf_names, [])
    add("pdf_hash", pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF))
    add("pdf_size", pdf_entry.get("size_bytes") == PDF.stat().st_size, pdf_entry.get("size_bytes"), PDF.stat().st_size)
    add("pdf_overfull", pdf_entry.get("overfull_hbox_count") == 0, pdf_entry.get("overfull_hbox_count"), 0)
    add("pdf_form_check", pdf_entry.get("form_check") == "PASS", pdf_entry.get("form_check"), "PASS")
    add("pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")

    # Public authority surfaces.
    surfaces = {
        "results": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "claim_status": CLAIM_DIR / "status.json",
        "claim_card": CLAIM_DIR / "claim.md",
        "roadmap": REPO / "ROADMAP.md",
        "todo": REPO / "TODO.md",
        "main_line": REPO / "theory/main-proof-line.md",
        "sector_readme": REPO / "theory/sector-A-foundation/README.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "changelog": REPO / "CHANGELOG.md",
    }
    surface_text: dict[str, str] = {}
    for label, path in surfaces.items():
        surface_text[label] = path.read_text(encoding="utf-8") if path.exists() else ""
        add(f"surface_{label}_r094", "R-094" in surface_text[label], "R-094" in surface_text[label], True)
    add("results_anchor", '<a id="r-094"></a>' in surface_text["results"], '<a id="r-094"></a>' in surface_text["results"], True)
    for negative in NEGATIVE_RESULTS:
        anchor = negative.lower()
        add(f"negative_{anchor}_registry", negative in surface_text["negative"] and f'<a id="{anchor}"></a>' in surface_text["negative"], negative in surface_text["negative"], True)

    # Append-only exploration records.
    exploration_path = REPO / "explorations/log.jsonl"
    exploration_records: dict[str, dict[str, Any]] = {}
    if exploration_path.exists():
        for line in exploration_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                if record.get("id") in EXPLORATIONS:
                    exploration_records[record["id"]] = record
    for exploration_id in EXPLORATIONS:
        record = exploration_records.get(exploration_id, {})
        add(f"exploration_{exploration_id}_exists", bool(record), bool(record), True)
        add(f"exploration_{exploration_id}_verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration_id], record.get("verdict"), EXPLORATION_VERDICTS[exploration_id])
        add(f"exploration_{exploration_id}_result_ref", "R-094" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), ["R-094"])

    add("manifest_schema", manifest.get("schema") == "tect/a13-root-local-gram-secant-feedback-boundary/1.0", manifest.get("schema"), "tect/a13-root-local-gram-secant-feedback-boundary/1.0")
    add("manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest_result_ledger", manifest.get("consequence", {}).get("result_ledger_id") == "R-094", manifest.get("consequence", {}).get("result_ledger_id"), "R-094")
    consequence = manifest.get("consequence", {})
    for key in ("complete_h_n", "reg", "full_overlap_src", "nelson", "interacting_measure", "sector_a_closure"):
        add(f"manifest_open_{key}", consequence.get(key) is False, consequence.get(key), False)
    add("manifest_centered_secant", consequence.get("regular_centered_gram_secant") is True, consequence.get("regular_centered_gram_secant"), True)
    add("manifest_prefix_payment", consequence.get("value_heat_control_prefix_payment") is True, consequence.get("value_heat_control_prefix_payment"), True)
    add("manifest_tier_stable", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest_negative_set", manifest.get("negative_results") == list(NEGATIVE_RESULTS), manifest.get("negative_results"), list(NEGATIVE_RESULTS))
    add("manifest_exploration_set", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))

    # Two terminal contract rows are appended below.  Pin the final integrated
    # count, not the intermediate length after only the first row.
    final_integrated_total = len(rows) + 2
    expected_integrated = contract.get("integrated_assertions")
    add("integrated_count_contract", count_only or final_integrated_total == expected_integrated, final_integrated_total, expected_integrated)
    primary_total = child_records.get("primary", {}).get("assertions_total", 0)
    independent_total = child_records.get("independent", {}).get("assertions_total", 0)
    aggregate_expected = contract.get("aggregate_assertions")
    final_aggregate_total = primary_total + independent_total + final_integrated_total
    add("aggregate_count_contract", count_only or final_aggregate_total == aggregate_expected, final_aggregate_total, aggregate_expected)

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-root-local-gram-secant-feedback-boundary-integrated/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "assertion_summary": {
            "primary": primary_total,
            "independent": independent_total,
            "integrated": len(rows),
            "aggregate": primary_total + independent_total + len(rows),
        },
        "failures": [row["name"] for row in failures],
        "boundary": {
            "regular_centered_gram_secant": True,
            "value_heat_control_prefix_payment": True,
            "rootwise_packet_embedding": False,
            "complete_h_n": False,
            "reg": False,
            "nelson": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if count_only:
        print(f"R-094 COUNT-ONLY integrated={len(rows)} aggregate={primary_total + independent_total + len(rows)}")
        return 0
    print(
        f"R-094 INTEGRATED {'PASS' if not failures else 'FAIL'}: "
        f"{len(rows) - len(failures)}/{len(rows)} integrated; "
        f"aggregate={primary_total + independent_total + len(rows)}"
    )
    if failures:
        print("failures=" + ",".join(row["name"] for row in failures))
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
