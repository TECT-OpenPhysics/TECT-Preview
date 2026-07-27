#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-100 A13 package."""

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
RESULT_ID = "A13-CLASSII-OWNER-GAUGE-HEAT-CENTERED-COVARIANCE-DEBT-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_owner_gauge_heat_centered_covariance_debt_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_owner_gauge_heat_centered_covariance_debt_reduction_independent.py"
NOTE = CLAIM_DIR / "notes/classii-owner-gauge-heat-centered-covariance-debt-reduction-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-owner-gauge-heat-centered-covariance-debt-reduction-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-owner-gauge-heat-centered-covariance-debt-reduction/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-owner-gauge-heat-centered-covariance-debt-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-owner-gauge-heat-centered-covariance-debt-reduction/result.json"

AUTHORITY = {
    "r079": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r094": (
        CLAIM_DIR / "classii_root_local_gram_secant_feedback_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-root-local-gram-secant-feedback-boundary/result.json",
    ),
    "r097": (
        CLAIM_DIR / "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-global-gram-terminalization-covariance-deficit-reduction/result.json",
    ),
    "r098": (
        CLAIM_DIR / "classii_signed_first_cartan_rational_ridge_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-signed-first-cartan-rational-ridge-boundary/result.json",
    ),
    "r099": (
        CLAIM_DIR / "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-27-integrated-extended-state-cartan-doob-rational-recovery/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "NG-2026-07-27-A13-COMPLETE-OWNER-CROSS-ROW-SCHUR-RESERVE",
    "NG-2026-07-27-A13-ABSTRACT-FIBRE-XY-COVARIANCE-DEBT",
)
EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(235, 243))
EXPLORATION_VERDICTS = {
    "EXP-000235": "advanced",
    "EXP-000236": "failed",
    "EXP-000237": "advanced",
    "EXP-000238": "advanced",
    "EXP-000239": "advanced",
    "EXP-000240": "failed",
    "EXP-000241": "inconclusive",
    "EXP-000242": "inconclusive",
}
NOTE_TOKENS = (
    "R-100",
    "evidence-anchor: theorem-2.1-complete-owner-gauge-collapse",
    "independent of $R$",
    "evidence-anchor: theorem-3.1-exact-complete-owner-row-additivity",
    "D_{\\rm row}",
    "Finer revelation transfers exactly the same mass",
    "evidence-anchor: theorem-4.1-posterior-covariance-debt-normal-form",
    "\\mathcal T={1\\over2}",
    "evidence-anchor: theorem-5.1-heat-centered-full-wick-residual",
    "2G_{j-1}\\mathbin\\odot d_j",
    "15(\\operatorname{tr}C)^3",
    "Young slack $1/3$",
    "evidence-anchor: theorem-6.1-abstract-xy-covariance-debt-no-go",
    "-{9m^2\\over400P}",
    "3/57800",
    "NG-2026-07-27-A13-COMPLETE-OWNER-CROSS-ROW-SCHUR-RESERVE",
    "NG-2026-07-27-A13-ABSTRACT-FIBRE-XY-COVARIANCE-DEBT",
    "T4 / T4; no promotion",
    "Sector-A closure",
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
    status = str(record.get("status", "")).upper()
    verdict = str(record.get("verdict", "")).upper()
    total = record.get("assertions_total")
    passed = record.get("assertions_passed")
    failed = record.get("assertions_failed")
    if status == "PASS" and isinstance(total, int) and total > 0:
        return passed == total and (failed is None or failed == 0)
    if verdict.endswith("PASS") or record.get("pass") is True:
        return True
    summary = record.get("summary", {})
    return isinstance(summary, dict) and summary.get("failed") == 0 and summary.get("passed", 0) > 0


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
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    records: dict[str, dict[str, Any]] = {}
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
        add("execution", f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add("execution", f"{label}_fresh_result", result_path.is_file(), repo_path(result_path), "fresh atomic output")
        try:
            record = load_json(result_path)
        except Exception as error:
            record = {}
            add("execution", f"{label}_result_json", False, repr(error), "valid JSON")
        else:
            add("execution", f"{label}_result_json", True, "valid JSON", "valid JSON")
        records[label] = record
        add("execution", f"{label}_passes", result_passes(record), record.get("status"), "PASS")
        add("execution", f"{label}_claim_id", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add("execution", f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records["primary"]
    independent = records["independent"]
    primary_names = (
        "owner_endpoint_identity_0",
        "matched_ridge_invariance_0",
        "complete_owner_row_additivity_0",
        "schur_gap_exact_cancellation_0",
        "row_posterior_gap_fraction",
        "complete_owner_refinement_invariance",
        "minimal_reveal_owner_identity",
        "F_equals_L_plus_H_3",
        "full_wick_increment_formula_2",
        "residual_cross_tower_identity_2",
        "gaussian_sixth_moment_bound_0",
        "tail_kernel_l1",
        "owner_diverges_with_bounded_y",
        "rational_quadratic_coefficient_exact",
        "infinitesimal_reserve_ratio",
    )
    independent_names = (
        "exact_owner_endpoint",
        "exact_ridge_invariance",
        "complete_owner_additive",
        "owner_refinement_invariant",
        "minimal_owner",
        "F_L_H_exact_3",
        "increment_formula_2",
        "tower_cross_2",
        "sixth_moment_ratio_0",
        "young_slack_exact",
        "negative_divergence",
        "quadratic_coefficient",
        "reserve_ratio",
    )
    for label, record, names in (
        ("primary", primary, primary_names),
        ("independent", independent, independent_names),
    ):
        for name in names:
            row = assertion(record, name)
            add("load_bearing", f"{label}_{name}", row.get("status") == "PASS", row.get("status"), "PASS")

    imports = imported_roots(INDEPENDENT)
    forbidden = sorted(imports & {"numpy", "sympy", PRIMARY.stem})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "independent_forbidden_imports", not forbidden, forbidden, [])
    add("independence", "independent_no_primary_text_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "independent_fraction_engine", "from fractions import Fraction" in independent_text and "def inverse(" in independent_text, "Fraction + inverse", "Fraction + inverse")

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_json", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_json", True, "valid JSON", "valid JSON")
    add("manifest", "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest_tier_t4", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve()), ("proof_note", NOTE)):
        entry = sources.get(label, {}) if isinstance(sources.get(label), dict) else {}
        add("manifest", f"manifest_{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        expected_hash = digest(path) if path.is_file() else "file"
        add("manifest", f"manifest_{label}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        expected_version = "1.0" if label == "proof_note" else source_version(path)
        add("manifest", f"manifest_{label}_version", entry.get("version") == expected_version, entry.get("version"), expected_version)

    authority_root = manifest.get("authority", {}) if isinstance(manifest.get("authority"), dict) else {}
    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        authority_entry = authority_root.get(label, {}) if isinstance(authority_root.get(label), dict) else {}
        for kind, path in (("manifest", authority_manifest), ("result", authority_result)):
            entry = authority_entry.get(kind, {}) if isinstance(authority_entry, dict) else {}
            add("authority", f"{label}_{kind}_exists", path.is_file(), repo_path(path), "file")
            add("authority", f"{label}_{kind}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
            expected_hash = digest(path) if path.is_file() else "file"
            add("authority", f"{label}_{kind}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        try:
            authority_record = load_json(authority_result)
        except Exception as error:
            add("authority", f"{label}_result_pass", False, repr(error), "PASS")
        else:
            add("authority", f"{label}_result_pass", result_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.is_file() else ""
    add("proof_note", "note_exists", NOTE.is_file(), repo_path(NOTE), "file")
    for index, token in enumerate(NOTE_TOKENS):
        add("proof_note", f"note_token_{index:02d}", token in note_text, token if token in note_text else "missing", token)
    add("proof_note", "note_no_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
    add("proof_note", "note_no_bare_qquad", "qquad" not in note_text.replace("\\qquad", ""), "clean" if "qquad" not in note_text.replace("\\qquad", "") else "bare qquad", "clean")
    add("proof_note", "note_fragment", "\\documentclass" not in note_text, "fragment", "fragment")

    add("proof_pdf", "pdf_exists", PDF.is_file(), repo_path(PDF), "file")
    pdf_page_count = 0
    pdf_text = ""
    pdf_fields = -1
    if PDF.is_file():
        reader = PdfReader(PDF)
        pdf_page_count = len(reader.pages)
        pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        pdf_fields = len(reader.get_fields() or {})
    add("proof_pdf", "pdf_page_count", pdf_page_count == 9, pdf_page_count, 9)
    add("proof_pdf", "pdf_no_fields", pdf_fields == 0, pdf_fields, 0)
    add("proof_pdf", "pdf_title", "Owner gauge, heat-centred full-Wick reveal" in pdf_text, "title" if "Owner gauge, heat-centred full-Wick reveal" in pdf_text else "missing", "title")
    add("proof_pdf", "pdf_footer", "R-100" in pdf_text and "Sector-A closure" in pdf_text, ["R-100" in pdf_text, "Sector-A closure" in pdf_text], [True, True])
    add("proof_pdf", "pdf_no_bare_qquad", "qquad" not in pdf_text, pdf_text.count("qquad"), 0)
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_pdf_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_pdf_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pdf_pages", proof_pdf.get("pages") == 9, proof_pdf.get("pages"), 9)
    add("proof_pdf", "manifest_pdf_form", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
    add("proof_pdf", "manifest_pdf_overfull", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_pdf_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative in NEGATIVE_RESULTS:
        anchor = negative.lower()
        add("negative_results", f"{anchor}_id", negative in registry_text, negative if negative in registry_text else "missing", negative)
        add("negative_results", f"{anchor}_anchor", f'<a id="{anchor}"></a>' in registry_text, anchor, "anchor")

    exploration_rows: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("id") in EXPLORATIONS:
            exploration_rows[record["id"]] = record
    for exploration in EXPLORATIONS:
        record = exploration_rows.get(exploration, {})
        add("explorations", f"{exploration}_present", bool(record), record.get("id"), exploration)
        add("explorations", f"{exploration}_verdict", record.get("verdict") == EXPLORATION_VERDICTS[exploration], record.get("verdict"), EXPLORATION_VERDICTS[exploration])
        add("explorations", f"{exploration}_result_ref", "R-100" in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), "contains R-100")

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-100", RESULT_ID, "Heat-centred full-Wick residual")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "EXP-000235", "EXP-000242", "3/57800")),
        "gates": (REPO / "claims/GATES.md", ("R-100", "D_H<=M_H+2 eta X+2 zeta Y+C")),
        "roadmap": (REPO / "ROADMAP.md", ("R-080--R-100", "heat-centred split")),
        "todo": (REPO / "TODO.md", ("R-100", "moving heat-baseline")),
        "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-100", "classii-owner-gauge-heat-centered-covariance-debt-reduction")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-100", "EXP-000242")),
    }
    for label, (path, tokens) in surface_tokens.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        add("surfaces", f"{label}_exists", path.is_file(), repo_path(path), "file")
        for index, token in enumerate(tokens):
            add("surfaces", f"{label}_token_{index}", token in text, token if token in text else "missing", token)

    try:
        status = load_json(CLAIM_DIR / "status.json")
    except Exception as error:
        status = {}
        add("surfaces", "status_json", False, repr(error), "valid JSON")
    else:
        add("surfaces", "status_json", True, "valid JSON", "valid JSON")
    add("surfaces", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    add("surfaces", "status_statement_r100", "R-100" in status.get("statement", ""), "R-100" if "R-100" in status.get("statement", "") else "missing", "R-100")
    add("surfaces", "status_reproduction", "owner_gauge_heat_centered_covariance_debt_reduction_verify.py" in status.get("reproduction", {}).get("command", ""), status.get("reproduction", {}).get("command"), "R-100 verifier")
    add("surfaces", "status_frontier", "moving heat-baseline" in status.get("next_action", "") and "Sector A remain open" in status.get("statement", ""), ["moving heat-baseline" in status.get("next_action", ""), "Sector A remain open" in status.get("statement", "")], [True, True])
    add("surfaces", "status_explorations", "EXP-000235--EXP-000242" in status.get("notes", ""), status.get("notes", "")[-120:], "EXP-000235--EXP-000242")

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total"), contract.get("primary_assertions"), primary.get("assertions_total"))
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total"), contract.get("independent_assertions"), independent.get("assertions_total"))
    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "complete_owner_payment_gauge_invariance": True,
        "complete_owner_row_additivity": True,
        "cross_row_schur_extra_reserve": False,
        "revelation_free_reserve": False,
        "posterior_covariance_debt_normal_form": True,
        "regular_heat_centered_full_wick_residual": True,
        "moving_heat_baseline_covariance_debt_bound": False,
        "rational_shifted_hessian_form": False,
        "complete_h_n": False,
        "reg": False,
        "full_overlap_src": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)
    final_integrated_count = len(rows) + 1
    add("contract", "integrated_count", contract.get("integrated_assertions") == final_integrated_count, contract.get("integrated_assertions"), final_integrated_count)

    passed = sum(row["status"] == "PASS" for row in rows)
    if count_only:
        print(f"INTEGRATED ASSERTIONS PLANNED: {len(rows)}")
        print(f"CURRENT PASS: {passed}/{len(rows)}")
        return 0
    payload = {
        "schema": "tect/a13-owner-gauge-heat-centered-covariance-debt-reduction-integrated/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "source_hashes": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "verifier": digest(Path(__file__).resolve()),
            "proof_note": digest(NOTE),
            "proof_pdf": digest(PDF),
            "manifest": digest(MANIFEST),
        },
        "authority_hashes": {
            label: {"manifest": digest(paths[0]), "result": digest(paths[1])}
            for label, paths in AUTHORITY.items()
        },
        "run_summary": {
            "primary": primary.get("assertions_total"),
            "independent": independent.get("assertions_total"),
            "integrated": len(rows),
            "aggregate": primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows),
        },
        "no_overclaim": (
            "R-100 certifies the exact owner-gauge/row/revelation algebra and regular "
            "heat-centred full-Wick residual. The moving production heat-baseline debt "
            "bound, rational (6.5), H_N, REG, OVERLAP_src, Nelson, measure, and Sector A remain open."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
