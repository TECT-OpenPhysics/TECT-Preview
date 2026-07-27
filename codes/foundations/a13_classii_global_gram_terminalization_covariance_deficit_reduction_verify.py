#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-097 A13 package."""

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
RESULT_ID = "A13-CLASSII-GLOBAL-GRAM-TERMINALIZATION-COVARIANCE-DEFICIT-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_global_gram_terminalization_covariance_deficit_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_global_gram_terminalization_covariance_deficit_reduction_independent.py"
NOTE = CLAIM_DIR / "notes/classii-global-gram-terminalization-covariance-deficit-reduction-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-global-gram-terminalization-covariance-deficit-reduction-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-global-gram-terminalization-covariance-deficit-reduction/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-global-gram-terminalization-covariance-deficit-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-global-gram-terminalization-covariance-deficit-reduction/result.json"

AUTHORITY = {
    "r063": (
        CLAIM_DIR / "classii_coefficient_jet_forest_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-coefficient-jet-forest-classification/result.json",
    ),
    "r066": (
        CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json",
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
    "r087": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r093": (
        CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-augmented-perspective-gibbs-gap-information-boundary/result.json",
    ),
    "r095": (
        CLAIM_DIR / "classii_fractional_feedback_square_perspective_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-fractional-feedback-square-perspective-boundary/result.json",
    ),
    "r096": (
        CLAIM_DIR / "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-low-hermite-wick-predictable-baseline-reduction/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "NG-2026-07-27-A13-PREDICTABILITY-ONLY-LOW-HERMITE-AGGREGATE",
    "NG-2026-07-27-A13-AUTOMATIC-POSTERIOR-COVARIANCE-POSITIVITY",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(214, 221))
EXPLORATION_VERDICTS = {
    "EXP-000214": "advanced",
    "EXP-000215": "advanced",
    "EXP-000216": "advanced",
    "EXP-000217": "advanced",
    "EXP-000218": "failed",
    "EXP-000219": "failed",
    "EXP-000220": "inconclusive",
}
NOTE_TOKENS = (
    "R-097",
    "evidence-anchor: theorem-3.1-complete-gram-row-heat-telescope",
    "complete Gram-row heat martingale",
    "evidence-anchor: theorem-5.1-terminal-theta-zero-schur",
    "terminal $\\theta=0$ Schur identity",
    "evidence-anchor: theorem-6.1-posterior-covariance-normal-form",
    "posterior-covariance bracket identity",
    "Derivative-free predictable terminalization",
    "predictability alone is insufficient",
    "Automatic positivity is false",
    "evidence-anchor: corollary-9.2-full-frame-integrated-successor",
    "Cartan root budget R-085 (4.11)",
    "Devil's-advocate self-test",
    "Result footer",
    "Sector A remain open",
    "T4 / T4; no promotion",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
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
    total = record.get("assertions_total")
    passed = record.get("assertions_passed")
    if record.get("status") == "PASS" and isinstance(total, int) and total > 0:
        failed = record.get("assertions_failed")
        if failed is None:
            rows = record.get("assertions", [])
            failed = sum(
                1
                for row in rows
                if isinstance(row, dict)
                and (row.get("status") == "FAIL" or row.get("ok") is False)
            )
        return passed == total and failed == 0
    verdict = str(record.get("verdict", "")).upper()
    for key in ("assertion_summary", "summary"):
        summary = record.get(key, {})
        if (
            isinstance(summary, dict)
            and isinstance(summary.get("total"), int)
            and summary.get("total", 0) > 0
            and summary.get("passed") == summary.get("total")
            and summary.get("failed") == 0
            and (verdict == "PASS" or verdict.endswith("-PASS"))
        ):
            return True
    return False


def result_total(record: dict[str, Any]) -> int:
    total = record.get("assertions_total")
    if isinstance(total, int):
        return total
    summary = record.get("assertion_summary", {})
    return summary.get("total", 0) if isinstance(summary, dict) else 0


def assertion(record: dict[str, Any], name: str) -> dict[str, Any]:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row
    return {}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main() -> int:
    count_only = "--count-only" in sys.argv
    rows: list[dict[str, Any]] = []

    def add(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"group": group, "name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    records: dict[str, dict[str, Any]] = {}
    for label, script, result_path in (
        ("primary", PRIMARY, PRIMARY_RESULT),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT),
    ):
        result_path.unlink(missing_ok=True)
        completed = subprocess.run([sys.executable, str(script)], cwd=REPO, capture_output=True, text=True, errors="replace", timeout=180)
        add("execution", f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add("execution", f"{label}_fresh_result", result_path.exists(), repo_path(result_path), "fresh atomic output")
        try:
            record = load_json(result_path)
        except Exception as error:
            record = {}
            add("execution", f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add("execution", f"{label}_result_load", True, "valid JSON", "valid JSON")
        records[label] = record
        add("execution", f"{label}_result_pass", result_passes(record), record.get("status", record.get("verdict")), "all assertions PASS")
        add("execution", f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add("execution", f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records["primary"]
    independent = records["independent"]
    for name in (
        "two_shell_predictable_endpoint_telescope",
        "terminal_schur_identity_0",
        "conditional_normal_form",
        "conditional_j_b_variance_certificate",
        "q_r_covariance_identity",
        "predictable_terminalization",
        "pi1_pi2_exhaust_wick_increment",
        "repeated_h2_norm_8",
        "rademacher_completed_minimum_negative",
        "gaussian_forest_h4",
        "moving_perspective_negative_defect",
        "future_leaking_control_rejected",
        "omitted_pi2_rejected",
    ):
        row = assertion(primary, name)
        add("primary_certificates", f"primary_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")
    for name in (
        "block_determinant",
        "expectation_endpoint_telescope",
        "future_leak_rejected",
        "product_reconstruction",
        "every_omission_detected",
        "unconditional_q_r_normal_form",
        "posterior_bracket_identity",
        "weighted_posterior_covariance_deficit_negative",
        "measured_h2_aggregate_norm_8",
        "naive_linear_aggregate_norm_rejected",
        "moving_base_defect_negative",
    ):
        row = assertion(independent, name)
        add("independent_certificates", f"independent_{name}", row.get("status") == "PASS", row.get("actual"), "PASS")

    independent_roots = imported_roots(INDEPENDENT) if INDEPENDENT.exists() else set()
    independent_text = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.exists() else ""
    add("independence", "independent_no_numpy", "numpy" not in independent_roots, sorted(independent_roots), "no numpy")
    add("independence", "independent_no_scipy", "scipy" not in independent_roots, sorted(independent_roots), "no scipy")
    add("independence", "independent_no_numerical_module_import", not any("global_gram_terminalization_covariance_deficit_reduction" in root for root in independent_roots), sorted(independent_roots), "no package source import")
    add("independence", "independent_no_primary_result_read", "primary-global-gram-terminalization" not in independent_text, "primary-global-gram-terminalization" in independent_text, False)
    declaration = independent.get("independence", {})
    add("independence", "independent_declares_stdlib", declaration.get("stdlib_only") is True, declaration.get("stdlib_only"), True)
    add("independence", "independent_declares_no_numerical_import", declaration.get("numerical_verifier_imported") is False, declaration.get("numerical_verifier_imported"), False)

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_load", True, "valid JSON", "valid JSON")

    authority_manifest = manifest.get("authority", {})
    for label, (manifest_path, result_path) in AUTHORITY.items():
        for kind, path in (("manifest", manifest_path), ("result", result_path)):
            expected_hash = authority_manifest.get(label, {}).get(kind, {}).get("sha256")
            actual_hash = digest(path) if path.exists() else None
            add("authority", f"authority_{label}_{kind}_exists", path.exists(), repo_path(path), "exists")
            add("authority", f"authority_{label}_{kind}_hash", actual_hash == expected_hash, actual_hash, expected_hash)
        try:
            authority_result = load_json(result_path)
        except Exception as error:
            add("authority", f"authority_{label}_pass", False, repr(error), "accepted PASS")
        else:
            add("authority", f"authority_{label}_pass", result_passes(authority_result), authority_result.get("status", authority_result.get("verdict")), "accepted PASS")

    source_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__).resolve(), "proof_note": NOTE}
    manifest_sources = manifest.get("sources", {})
    for label, path in source_paths.items():
        entry = manifest_sources.get(label, {})
        add("hashes", f"source_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        add("hashes", f"source_{label}_hash", path.exists() and entry.get("sha256") == digest(path), entry.get("sha256"), digest(path) if path.exists() else None)
        if label != "proof_note":
            add("hashes", f"source_{label}_version", entry.get("version") == source_version(path), entry.get("version"), source_version(path))

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    note_words = " ".join(note_text.split())
    for index, token in enumerate(NOTE_TOKENS):
        token_words = " ".join(token.split())
        add("note", f"note_token_{index:02d}", token_words in note_words, token_words in note_words, True)
    has_hangul = any(0xAC00 <= ord(character) <= 0xD7AF for character in note_text)
    add("note", "note_english_only", not has_hangul, has_hangul, False)

    try:
        reader = PdfReader(PDF)
        pdf_pages = len(reader.pages)
        page_lengths = [len((page.extract_text() or "").strip()) for page in reader.pages]
        pdf_forms = bool(reader.get_fields())
        pdf_encrypted = reader.is_encrypted
        root_text = str(reader.trailer.get("/Root", {}))
    except Exception as error:
        pdf_pages, page_lengths, pdf_forms, pdf_encrypted, root_text = 0, [], True, True, "/JavaScript"
        add("pdf", "pdf_load", False, repr(error), "readable PDF")
    else:
        add("pdf", "pdf_load", True, "readable PDF", "readable PDF")
    pdf_entry = manifest.get("proof_pdf", {})
    add("pdf", "pdf_pages", pdf_pages == pdf_entry.get("pages") and pdf_pages > 0, pdf_pages, pdf_entry.get("pages"))
    add("pdf", "pdf_nonblank_pages", bool(page_lengths) and min(page_lengths) > 100, page_lengths, "each page >100 characters")
    add("pdf", "pdf_no_forms", not pdf_forms, pdf_forms, False)
    add("pdf", "pdf_not_encrypted", not pdf_encrypted, pdf_encrypted, False)
    add("pdf", "pdf_no_javascript", "/JavaScript" not in root_text and "/JS" not in root_text, [token for token in ("/JavaScript", "/JS") if token in root_text], [])
    add("pdf", "pdf_hash", PDF.exists() and pdf_entry.get("sha256") == digest(PDF), pdf_entry.get("sha256"), digest(PDF) if PDF.exists() else None)
    add("pdf", "pdf_size", PDF.exists() and pdf_entry.get("size_bytes") == PDF.stat().st_size, pdf_entry.get("size_bytes"), PDF.stat().st_size if PDF.exists() else None)
    add("pdf", "pdf_overfull", pdf_entry.get("overfull_hbox_count") == 0, pdf_entry.get("overfull_hbox_count"), 0)
    add("pdf", "pdf_form_check", pdf_entry.get("form_check") == "PASS", pdf_entry.get("form_check"), "PASS")
    add("pdf", "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")

    surfaces = {
        "results": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "claim_status": CLAIM_DIR / "status.json",
        "claim_card": CLAIM_DIR / "claim.md",
        "roadmap": REPO / "ROADMAP.md",
        "gates": REPO / "claims/GATES.md",
        "todo": REPO / "TODO.md",
        "main_line": REPO / "theory/main-proof-line.md",
        "sector_readme": REPO / "theory/sector-A-foundation/README.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "changelog": REPO / "CHANGELOG.md",
    }
    surface_text: dict[str, str] = {}
    for label, path in surfaces.items():
        surface_text[label] = path.read_text(encoding="utf-8") if path.exists() else ""
        add("surfaces", f"surface_{label}_r097", "R-097" in surface_text[label], "R-097" in surface_text[label], True)
    add("surfaces", "results_anchor", '<a id="r-097"></a>' in surface_text["results"], '<a id="r-097"></a>' in surface_text["results"], True)
    for negative in NEGATIVE_RESULTS:
        anchor = negative.lower()
        add("surfaces", f"negative_{anchor}", negative in surface_text["negative"] and f'<a id="{anchor}"></a>' in surface_text["negative"], negative in surface_text["negative"], True)

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
        add("explorations", f"exploration_{exploration_id}_exists", bool(record), bool(record), True)
        add("explorations", f"exploration_{exploration_id}_verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration_id], record.get("verdict"), EXPLORATION_VERDICTS[exploration_id])
        add("explorations", f"exploration_{exploration_id}_result_ref", "R-097" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), ["R-097"])

    consequence = manifest.get("consequence", {})
    add("manifest", "manifest_schema", manifest.get("schema") == "tect/a13-global-gram-terminalization-covariance-deficit-reduction/1.0", manifest.get("schema"), "tect/a13-global-gram-terminalization-covariance-deficit-reduction/1.0")
    add("manifest", "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest_ledger", consequence.get("result_ledger_id") == "R-097", consequence.get("result_ledger_id"), "R-097")
    for key in ("rational_heat_telescope", "terminal_theta_zero_schur", "posterior_covariance_normal_form", "derivative_free_doob_terminalization"):
        add("manifest", f"manifest_proved_{key}", consequence.get(key) is True, consequence.get(key), True)
    for key in ("production_covariance_bracket_bound", "cartan_one_use", "complete_h_n", "reg", "full_progressive_revisit", "full_overlap_src", "nelson", "interacting_measure", "sector_a_closure"):
        add("manifest", f"manifest_open_{key}", consequence.get(key) is False, consequence.get(key), False)
    add("manifest", "manifest_tier_stable", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "manifest_negative_set", manifest.get("negative_results") == list(NEGATIVE_RESULTS), manifest.get("negative_results"), list(NEGATIVE_RESULTS))
    add("manifest", "manifest_exploration_set", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))

    contract = manifest.get("run_contract", {})
    final_integrated_total = len(rows) + 2
    add("contract", "integrated_count_contract", count_only or final_integrated_total == contract.get("integrated_assertions"), final_integrated_total, contract.get("integrated_assertions"))
    primary_total = result_total(primary)
    independent_total = result_total(independent)
    final_aggregate = primary_total + independent_total + final_integrated_total
    add("contract", "aggregate_count_contract", count_only or final_aggregate == contract.get("aggregate_assertions"), final_aggregate, contract.get("aggregate_assertions"))

    failures = [row for row in rows if row["status"] != "PASS"]
    groups: dict[str, dict[str, int]] = {}
    for row in rows:
        summary = groups.setdefault(row["group"], {"total": 0, "passed": 0, "failed": 0})
        summary["total"] += 1
        summary["passed" if row["status"] == "PASS" else "failed"] += 1
    payload = {
        "schema": "tect/a13-global-gram-terminalization-covariance-deficit-reduction-integrated/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertion_groups": groups,
        "assertions": rows,
        "failures": [row["name"] for row in failures],
        "assertion_summary": {"primary": primary_total, "independent": independent_total, "integrated": len(rows), "aggregate": primary_total + independent_total + len(rows)},
        "boundary": {
            "rational_heat_telescope": True,
            "terminal_theta_zero_schur": True,
            "posterior_covariance_normal_form": True,
            "production_covariance_bracket_bound": False,
            "cartan_one_use_4_11": False,
            "complete_h_n": False,
            "reg": False,
            "nelson": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    if count_only:
        print(f"R-097 COUNT-ONLY integrated={len(rows)} aggregate={primary_total + independent_total + len(rows)}")
        return 0
    print(f"R-097 INTEGRATED {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)}; aggregate={primary_total + independent_total + len(rows)}")
    if failures:
        print("failures=" + ",".join(row["name"] for row in failures))
    print(f"output={repo_path(OUTPUT)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
