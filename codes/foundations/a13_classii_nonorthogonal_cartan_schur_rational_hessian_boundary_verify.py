#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-085 A13 boundary package."""

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
RESULT_ID = "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_nonorthogonal_cartan_schur_rational_hessian_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_nonorthogonal_cartan_schur_rational_hessian_boundary_independent.py"
MANIFEST = CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-nonorthogonal-cartan-schur-rational-shifted-hessian-boundary-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json"
EXPECTED_PRIMARY = 50
EXPECTED_INDEPENDENT = 36
# Updated once after the assertion surface is frozen. The final row checks its
# own count, so a later assertion edit fails closed until this contract changes.
EXPECTED_INTEGRATED = 130
EXPECTED_AGGREGATE = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED
EXPECTED_PAGES = 9
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "a1_production": (
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
        None,
    ),
    "r063_balanced_jet": (
        CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    ),
    "r071_one_form": (
        CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-one-form-sobolev-linear-closure/result.json",
    ),
    "r081_temporal": (
        CLAIM_DIR / "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-tail-adapted-near-temporal-reduction/result.json",
    ),
    "r082_stopped_current": (
        CLAIM_DIR / "classii_stopped_current_far_complete_current_near_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-stopped-current-far-complete-current-near/result.json",
    ),
    "r084_root_ou_linear": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-085", RESULT_ID, "shifted-Hessian", "five unshifted")),
    "roadmap": (REPO / "ROADMAP.md", ("R-085", "nonorthogonal", "shifted-Hessian", "Sector A remains open")),
    "gates": (REPO / "claims/GATES.md", ("R-085", "production atom", "shifted-Hessian")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "50/50", "36/36", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-085", RESULT_ID, "nonorthogonal", "shifted-Hessian")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-085", "Schur", "shifted-Hessian")),
    "todo": (REPO / "todo/todo.json", ("R-085", "mixed-Cartan atom", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-085", "production atom", "shifted-Hessian")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-085", "nonorthogonal", "shifted-Hessian")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-085", "Schur", "Hessian-plus-positive-square")),
    "sector": (REPO / "theory/sectors/A.md", ("shifted-Hessian", "RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR")),
    "negative_registry": (REPO / "negative-results/registry.md", ("NG-2026-07-25-A13-RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR", "not a form-bound counterexample")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000114", "EXP-000120", "R-085")),
    "changelog": (REPO / "CHANGELOG.md", ("R-085", "shifted-Hessian")),
}

NOTE_TOKENS = (
    "The complete Cartan mixed variation",
    "Theorem 4.1",
    "Nonorthogonal weighted causal Schur lemma",
    "Theorem 5.1 (exact endpoint)",
    "Theorem 6.1 (five-family form absorption)",
    "NG-2026-07-25-A13-RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR",
    "The four-stage completion map",
    "Proof-and-failure map",
    "No-overclaim statement",
)

PDF_TOKENS = (
    "Nonorthogonal weighted causal Schur lemma",
    "Exact rational endpoint",
    "five-family form absorption",
    "shifted Hessian cannot be deleted",
    "four-stage completion map",
    "Proof-and-failure map",
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
    return subprocess.run(
        [sys.executable, str(path)], cwd=REPO, capture_output=True, text=True,
        timeout=CHILD_TIMEOUT_SECONDS, check=False,
    )


def record_passes(record: dict[str, Any]) -> bool:
    rows = record.get("assertions")
    return (
        record.get("status") == "PASS"
        and isinstance(rows, list)
        and bool(rows)
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in rows)
    )


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

    child_specs = (
        ("primary", PRIMARY, PRIMARY_OUTPUT, f"[R-085 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, f"[R-085 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
    )
    records: dict[str, dict[str, Any]] = {}
    for label, child, output, marker, expected_count in child_specs:
        try:
            completed = run_child(child)
        except Exception as exc:
            completed = None
            failures.append(f"{label} execution: {exc}")
        output_text = "" if completed is None else completed.stdout + completed.stderr
        add(rows, f"{label}_exit_zero", completed is not None and completed.returncode == 0, None if completed is None else completed.returncode, 0)
        add(rows, f"{label}_marker", marker in output_text, output_text.strip(), marker)
        add(rows, f"{label}_result_exists", output.exists(), str(output.relative_to(REPO)), "exists")
        try:
            record = load_json(output)
        except Exception as exc:
            record = {}
            failures.append(f"{label} result: {exc}")
        records[label] = record
        add(rows, f"{label}_record_passes", record_passes(record), record.get("status"), "PASS with all rows")
        add(rows, f"{label}_count", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add(rows, f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-nonorthogonal-cartan-schur-rational-hessian-boundary-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-nonorthogonal-cartan-schur-rational-hessian-boundary-independent/1.0", independent.get("schema"), "independent/1.0")

    try:
        schur_delta = abs(float(primary["schur_result"]["constant"]) - float(independent["schur_constant"]))
    except Exception:
        schur_delta = float("inf")
    add(rows, "cross_schur_constant", schur_delta < 1e-12, schur_delta, "<1e-12")
    try:
        third_delta = abs(float(primary["rational_result"]["scalar_third_derivative"]) - float(independent["scalar_third_derivative"]))
    except Exception:
        third_delta = float("inf")
    add(rows, "cross_scalar_third_derivative", third_delta < 1e-10, third_delta, "<1e-10")
    try:
        hidden_delta = abs(float(primary["rational_result"]["hidden_q_pair_float"]) - float(independent["hidden_q_pair"]))
    except Exception:
        hidden_delta = float("inf")
    add(rows, "cross_hidden_q_pair", hidden_delta < 1e-14, hidden_delta, "<1e-14")
    for key in ("F0", "DR", "ratio"):
        try:
            delta = abs(float(primary["rational_result"]["fixed_schur_fixture"][key]) - float(independent["fixed_schur_fixture"][key]))
        except Exception:
            delta = float("inf")
        add(rows, f"cross_fixed_schur_{key}", delta < 1e-14, delta, "<1e-14")
    try:
        primary_matrix = [[float(Fraction(value)) for value in line] for line in primary["rational_result"]["normalized_shifted_hessian_remainder"]]
        independent_matrix = independent["rational_remainder"]
        matrix_delta = max(abs(primary_matrix[i][j] - independent_matrix[i][j]) for i in range(2) for j in range(2))
    except Exception:
        matrix_delta = float("inf")
    add(rows, "cross_shifted_hessian_matrix", matrix_delta < 1e-12, matrix_delta, "<1e-12")
    add(rows, "primary_five_degrees", primary.get("rational_result", {}).get("five_degrees") == ["7/20", "7/10", "13/30", "3/5", "23/30"], primary.get("rational_result", {}).get("five_degrees"), ["7/20", "7/10", "13/30", "3/5", "23/30"])
    add(rows, "primary_five_slacks", primary.get("rational_result", {}).get("five_slacks") == ["13/20", "3/10", "17/30", "2/5", "7/30"], primary.get("rational_result", {}).get("five_slacks"), ["13/20", "3/10", "17/30", "2/5", "7/30"])
    add(rows, "primary_candidate_is_conditional", "conditional" in str(primary.get("schur_result", {}).get("theorem_scope")), primary.get("schur_result", {}).get("theorem_scope"), "conditional")
    add(rows, "primary_reg_open", str(primary.get("synthesis", {}).get("REG", "")).startswith("open:"), primary.get("synthesis", {}).get("REG"), "open")
    add(rows, "primary_overlap_open", str(primary.get("synthesis", {}).get("OVERLAP", "")).startswith("open:"), primary.get("synthesis", {}).get("OVERLAP"), "open")
    add(rows, "primary_core_open", str(primary.get("synthesis", {}).get("CORE", "")).startswith("open:"), primary.get("synthesis", {}).get("CORE"), "open")
    add(rows, "primary_bd_conditional", "conditional" in str(primary.get("synthesis", {}).get("BD", "")), primary.get("synthesis", {}).get("BD"), "conditional")

    add(rows, "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_t4_open", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(rows, f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(rows, f"{label}_manifest_hash", authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest), pin.get("manifest", {}).get("sha256"), None if not authority_manifest.exists() else digest(authority_manifest))
        if authority_result is not None:
            add(rows, f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
            add(rows, f"{label}_result_hash", authority_result.exists() and pin.get("result", {}).get("sha256") == digest(authority_result), pin.get("result", {}).get("sha256"), None if not authority_result.exists() else digest(authority_result))
            try:
                authority_record = load_json(authority_result)
            except Exception:
                authority_record = {}
            authority_rows = authority_record.get("assertions") or authority_record.get("integrated_assertions") or authority_record.get("cross_assertions")
            authority_pass = authority_record.get("status") == "PASS" or authority_record.get("pass") is True or "PASS" in str(authority_record.get("verdict", ""))
            add(rows, f"{label}_result_passes", authority_pass and isinstance(authority_rows, list) and all(row.get("status") == "PASS" for row in authority_rows), authority_record.get("status", authority_record.get("verdict")), "PASS")

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
    control_chars = [ord(char) for char in note_text if ord(char) < 32 and char not in "\t\n\r"]
    add(rows, "note_no_control_chars", not control_chars, control_chars, [])
    add(rows, "note_no_literal_qquad", "qquad" not in note_text.replace("\\qquad", ""), "literal qquad absent", "absent")
    add(rows, "note_honesty_boundary", all(token in note_text for token in ("No production Cartan atom", "rational shifted-Hessian", "Sector A")), "open boundaries present", "present")

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
    add(rows, "pdf_pages", pages == EXPECTED_PAGES, pages, EXPECTED_PAGES)
    add(rows, "pdf_not_encrypted", not encrypted, encrypted, False)
    add(rows, "pdf_no_forms", not has_forms, has_forms, False)
    for index, token in enumerate(PDF_TOKENS, start=1):
        add(rows, f"pdf_token_{index}", token in pdf_text, token if token in pdf_text else None, token)
    pdf_pin = manifest.get("proof_pdf", {})
    add(rows, "pdf_hash", PDF.exists() and pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), None if not PDF.exists() else digest(PDF))
    add(rows, "pdf_size", PDF.exists() and pdf_pin.get("size_bytes") == PDF.stat().st_size, pdf_pin.get("size_bytes"), None if not PDF.exists() else PDF.stat().st_size)
    add(rows, "pdf_manifest_pages", pdf_pin.get("pages") == EXPECTED_PAGES, pdf_pin.get("pages"), EXPECTED_PAGES)
    add(rows, "pdf_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    add(rows, "pdf_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)

    for label, (path, tokens) in SURFACES.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(rows, f"surface_{label}_tokens", all(token in text for token in tokens), [token for token in tokens if token not in text], [])

    claims_not = manifest.get("claims_not_established", {})
    required_false = (
        "production_cartan_atom_estimate", "controlled_cartan_cfar", "rational_shifted_hessian_form_bound",
        "complete_signed_near", "complete_regular_packet_lower_bound", "full_progressive_revisit_extension",
        "controlled_shell_one_use", "nelson_bound", "interacting_measure", "sector_a_closure", "tier_promotion",
    )
    add(rows, "manifest_open_flags_false", all(claims_not.get(key) is False for key in required_false), {key: claims_not.get(key) for key in required_false}, "all false")
    consequence = manifest.get("consequence", {})
    add(rows, "manifest_nonorthogonal_schur_true", consequence.get("nonorthogonal_weighted_causal_schur") is True, consequence.get("nonorthogonal_weighted_causal_schur"), True)
    add(rows, "manifest_five_families_true", consequence.get("rational_five_unshifted_families_paid") is True, consequence.get("rational_five_unshifted_families_paid"), True)
    add(rows, "manifest_negative_registered", "NG-2026-07-25-A13-RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR" in manifest.get("negative_results", []), manifest.get("negative_results"), "contains R-085 no-go")
    run_contract = manifest.get("run_contract", {})
    add(
        rows,
        "manifest_run_counts",
        run_contract.get("primary_assertions") == EXPECTED_PRIMARY
        and run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT
        and run_contract.get("integrated_assertions") == EXPECTED_INTEGRATED
        and run_contract.get("aggregate_assertions") == EXPECTED_AGGREGATE
        and len(rows) + 1 == EXPECTED_INTEGRATED,
        run_contract,
        [EXPECTED_PRIMARY, EXPECTED_INDEPENDENT, EXPECTED_INTEGRATED, EXPECTED_AGGREGATE],
    )

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-nonorthogonal-cartan-schur-rational-hessian-boundary-integrated/1.0",
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
        "proved_scope": "manifest-pinned R-085 nonorthogonal weighted causal Schur implication and exact rational five-family/shifted-Hessian boundary",
        "open_scope": "production Cartan atom, rational shifted-Hessian bound, REG, OVERLAP, CORE, one-use, Nelson, measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-085 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-085 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
