#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-096 A13 reduction package."""

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
RESULT_ID = "A13-CLASSII-LOW-HERMITE-WICK-PREDICTABLE-BASELINE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_low_hermite_wick_predictable_baseline_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_low_hermite_wick_predictable_baseline_reduction_independent.py"
NOTE = CLAIM_DIR / "notes/classii-low-hermite-wick-predictable-baseline-reduction-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-low-hermite-wick-predictable-baseline-reduction-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-low-hermite-wick-predictable-baseline-reduction/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-low-hermite-wick-predictable-baseline-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-low-hermite-wick-predictable-baseline-reduction/result.json"

AUTHORITY = {
    "r063": (
        CLAIM_DIR / "classii_coefficient_jet_forest_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-coefficient-jet-forest-classification/result.json",
    ),
    "r077": (
        CLAIM_DIR / "classii_causal_packet_payload_resonance_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-causal-packet-payload-resonance/result.json",
    ),
    "r079": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r085": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
    "r086": (
        CLAIM_DIR / "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-rational-translated-wick-payload-comparable-reduction/result.json",
    ),
    "r095": (
        CLAIM_DIR / "classii_fractional_feedback_square_perspective_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-fractional-feedback-square-perspective-boundary/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "NG-2026-07-27-A13-PREDICTABLE-BASELINE-SUPPORT-IMPLIES-PAYABILITY",
    "NG-2026-07-27-A13-LOW-HERMITE-STEIN-DERIVATIVE-CLOSURE",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(207, 214))
EXPLORATION_VERDICTS = {
    "EXP-000207": "advanced",
    "EXP-000208": "advanced",
    "EXP-000209": "failed",
    "EXP-000210": "advanced",
    "EXP-000211": "failed",
    "EXP-000212": "advanced",
    "EXP-000213": "failed",
}

NOTE_TOKENS = (
    "R-096",
    "evidence-anchor: theorem-2.1-once-only-rational-embedding",
    "once-only rational-row embedding",
    "evidence-anchor: proposition-3.1-doob-product-commutator",
    "Doob/product commutator",
    "evidence-anchor: theorem-4.1-predictable-baseline-support-collapse",
    "genuine large-gap residual is empty",
    "evidence-anchor: theorem-5.1-low-hermite-wick-compression",
    "only ranks zero, one, and two survive",
    "evidence-anchor: fixture-6.1-smooth-mean-ownership",
    "evidence-anchor: proposition-7.1-unweighted-hermite-boundary",
    "The adapted-prefix frontier",
    "Devil's-advocate self-test",
    "Result footer",
    "Sector A, and",
    "T5--T7 remain open",
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


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def result_passes(record: dict[str, Any]) -> bool:
    passed = record.get("assertions_passed", record.get("passed"))
    total = record.get("assertions_total", record.get("assertion_count"))
    current_contract = (
        record.get("status") == "PASS"
        and isinstance(passed, int)
        and isinstance(total, int)
        and total > 0
        and passed == total
        and record.get("assertions_failed", record.get("failed", 0)) == 0
    )
    summary = record.get("summary", {})
    legacy_contract = (
        isinstance(summary, dict)
        and isinstance(summary.get("total"), int)
        and summary.get("total", 0) > 0
        and summary.get("passed") == summary.get("total")
        and summary.get("failed") == 0
        and str(record.get("verdict", "")).endswith("PASS")
    )
    return current_contract or legacy_contract


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("actual")
    return None


def assertion_passes(record: dict[str, Any], name: str) -> bool:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("status") == "PASS"
    return False


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def pdf_reachable_names(root: Any) -> set[str]:
    names: set[str] = set()
    seen: set[int] = set()

    def visit(node: Any) -> None:
        get_object = getattr(node, "get_object", None)
        if callable(get_object):
            resolved = get_object()
            if resolved is not node:
                visit(resolved)
                return
        if isinstance(node, dict):
            marker = id(node)
            if marker in seen:
                return
            seen.add(marker)
            for key, value in node.items():
                names.add(str(key))
                visit(value)
        elif isinstance(node, (list, tuple)):
            marker = id(node)
            if marker in seen:
                return
            seen.add(marker)
            for value in node:
                visit(value)
        elif isinstance(node, str) and node.startswith("/"):
            names.add(node)

    visit(root)
    return names


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
            record = load_json(result_path)
        except Exception as error:
            add(f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add(f"{label}_result_load", True, "valid JSON", "valid JSON")
            add(f"{label}_result_pass", result_passes(record), record.get("status"), "PASS with all assertions")
            add(f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
            add(f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    try:
        primary_record = load_json(PRIMARY_RESULT)
    except Exception:
        primary_record = {}
    try:
        independent_record = load_json(INDEPENDENT_RESULT)
    except Exception:
        independent_record = {}

    add("primary_low_hermite_identity", assertion_passes(primary_record, "one_root_low_hermite_identity"), assertion_actual(primary_record, "one_root_low_hermite_identity"), "PASS")
    add("primary_tensorized_identity", assertion_passes(primary_record, "tensorized_low_hermite_pairing"), assertion_actual(primary_record, "tensorized_low_hermite_pairing"), "PASS")
    add("primary_support_collapse", all(assertion_actual(primary_record, f"predictable_large_gap_empty_{cutoff}") == [] for cutoff in (-2, 0, 3, 7)), [assertion_actual(primary_record, f"predictable_large_gap_empty_{cutoff}") for cutoff in (-2, 0, 3, 7)], [[], [], [], []])
    add("primary_tanh_raw_zero", assertion_passes(primary_record, "tanh_raw_wick_zero"), assertion_actual(primary_record, "tanh_raw_wick_zero"), "PASS")
    add("primary_tanh_q_positive", assertion_passes(primary_record, "tanh_q_positive"), assertion_actual(primary_record, "tanh_q_positive"), "PASS")
    add("primary_tanh_r_positive", assertion_passes(primary_record, "tanh_r_positive"), assertion_actual(primary_record, "tanh_r_positive"), "PASS")
    add("independent_exact_tensor", assertion_passes(independent_record, "exact_tensorized_wick_identity"), assertion_actual(independent_record, "exact_tensorized_wick_identity"), "PASS")
    add("independent_selector_chain", assertion_passes(independent_record, "selector_chain_first_hermite"), assertion_actual(independent_record, "selector_chain_first_hermite"), "PASS")
    add("independent_support_collapse", all(assertion_actual(independent_record, f"independent_support_empty_{cutoff}") == [] for cutoff in (-3, 0, 5)), [assertion_actual(independent_record, f"independent_support_empty_{cutoff}") for cutoff in (-3, 0, 5)], [[], [], []])

    independent_modules = imported_modules(INDEPENDENT) if INDEPENDENT.exists() else set()
    independent_text = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.exists() else ""
    add("independent_no_numpy", "numpy" not in independent_modules, sorted(independent_modules), "no numpy import")
    add("independent_no_scipy", "scipy" not in independent_modules, sorted(independent_modules), "no scipy import")
    add("independent_no_primary_import", not any("low_hermite_wick_predictable_baseline_reduction" in module for module in independent_modules), sorted(independent_modules), "no primary import")
    add("independent_no_primary_result_read", "primary-low-hermite-wick" not in independent_text, "primary-low-hermite-wick" in independent_text, False)
    independence = independent_record.get("independence", {})
    add("independent_declares_no_primary_import", independence.get("imports_primary") is False, independence.get("imports_primary"), False)
    add("independent_declares_no_primary_read", independence.get("reads_primary_result") is False, independence.get("reads_primary_result"), False)

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest_load", True, "valid JSON", "valid JSON")
    contract = manifest.get("run_contract", {})

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
            add(f"authority_{label}_result_pass", result_passes(authority_result), authority_result.get("status"), "accepted PASS authority")

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
        add(f"source_{label}_hash", path.exists() and entry.get("sha256") == digest(path), entry.get("sha256"), digest(path) if path.exists() else None)
        if label != "proof_note":
            add(f"source_{label}_version", entry.get("version") == source_version(path), entry.get("version"), source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS):
        add(f"note_token_{index:02d}", token in note_text, token in note_text, True)
    hangul_ranges = ((0x1100, 0x11FF), (0x3130, 0x318F), (0xA960, 0xA97F), (0xAC00, 0xD7AF), (0xD7B0, 0xD7FF))
    has_hangul = any(any(lower <= ord(character) <= upper for lower, upper in hangul_ranges) for character in note_text)
    add("note_english_scope", not has_hangul, has_hangul, False)

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
    add("pdf_hash", PDF.exists() and pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF) if PDF.exists() else None)
    add("pdf_size", PDF.exists() and pdf_entry.get("size_bytes") == PDF.stat().st_size, pdf_entry.get("size_bytes"), PDF.stat().st_size if PDF.exists() else None)
    add("pdf_overfull", pdf_entry.get("overfull_hbox_count") == 0, pdf_entry.get("overfull_hbox_count"), 0)
    add("pdf_form_check", pdf_entry.get("form_check") == "PASS", pdf_entry.get("form_check"), "PASS")
    add("pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")

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
        add(f"surface_{label}_r096", "R-096" in surface_text[label], "R-096" in surface_text[label], True)
    add("results_anchor", '<a id="r-096"></a>' in surface_text["results"], '<a id="r-096"></a>' in surface_text["results"], True)
    for negative in NEGATIVE_RESULTS:
        anchor = negative.lower()
        add(f"negative_{anchor}_registry", negative in surface_text["negative"] and f'<a id="{anchor}"></a>' in surface_text["negative"], negative in surface_text["negative"], True)

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
        add(f"exploration_{exploration_id}_result_ref", "R-096" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), ["R-096"])

    add("manifest_schema", manifest.get("schema") == "tect/a13-low-hermite-wick-predictable-baseline-reduction/1.0", manifest.get("schema"), "tect/a13-low-hermite-wick-predictable-baseline-reduction/1.0")
    add("manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest_result_ledger", manifest.get("consequence", {}).get("result_ledger_id") == "R-096", manifest.get("consequence", {}).get("result_ledger_id"), "R-096")
    consequence = manifest.get("consequence", {})
    for key in (
        "complete_packet_ordering",
        "predictable_baseline_large_gap_empty",
        "low_hermite_compression",
        "full_square_mean_ownership",
    ):
        add(f"manifest_proved_{key}", consequence.get(key) is True, consequence.get(key), True)
    for key in (
        "adapted_prefix_payment",
        "positive_hermite_spatial_gain",
        "complete_h_n",
        "reg",
        "full_progressive_revisit",
        "full_overlap_src",
        "nelson",
        "interacting_measure",
        "sector_a_closure",
    ):
        add(f"manifest_open_{key}", consequence.get(key) is False, consequence.get(key), False)
    add("manifest_tier_stable", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest_negative_set", manifest.get("negative_results") == list(NEGATIVE_RESULTS), manifest.get("negative_results"), list(NEGATIVE_RESULTS))
    add("manifest_exploration_set", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))

    final_integrated_total = len(rows) + 2
    expected_integrated = contract.get("integrated_assertions")
    add("integrated_count_contract", count_only or final_integrated_total == expected_integrated, final_integrated_total, expected_integrated)
    primary_total = primary_record.get("assertions_total", 0)
    independent_total = independent_record.get("assertions_total", 0)
    aggregate_expected = contract.get("aggregate_assertions")
    final_aggregate_total = primary_total + independent_total + final_integrated_total
    add("aggregate_count_contract", count_only or final_aggregate_total == aggregate_expected, final_aggregate_total, aggregate_expected)

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-low-hermite-wick-predictable-baseline-reduction-integrated/1.0",
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
            "complete_packet_ordering": True,
            "predictable_baseline_large_gap_empty": True,
            "low_hermite_compression": True,
            "adapted_prefix_payment": False,
            "complete_h_n": False,
            "reg": False,
            "nelson": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if count_only:
        print(f"R-096 COUNT-ONLY integrated={len(rows)} aggregate={primary_total + independent_total + len(rows)}")
        return 0
    print(
        f"R-096 INTEGRATED {'PASS' if not failures else 'FAIL'}: "
        f"{len(rows) - len(failures)}/{len(rows)} integrated; "
        f"aggregate={primary_total + independent_total + len(rows)}"
    )
    if failures:
        print("failures=" + ",".join(row["name"] for row in failures))
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
