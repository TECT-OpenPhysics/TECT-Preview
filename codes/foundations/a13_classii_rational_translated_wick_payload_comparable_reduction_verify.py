#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-086 rational package."""

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
RESULT_ID = "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_rational_translated_wick_payload_comparable_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_rational_translated_wick_payload_comparable_reduction_independent.py"
MANIFEST = CLAIM_DIR / "classii_rational_translated_wick_payload_comparable_reduction_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-rational-translated-wick-payload-comparable-reduction-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-rational-translated-wick-payload-comparable-reduction/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-rational-translated-wick-payload-comparable-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-rational-translated-wick-payload-comparable-reduction/result.json"
EXPECTED_PRIMARY = 39
EXPECTED_INDEPENDENT = 38
EXPECTED_INTEGRATED = 127
EXPECTED_AGGREGATE = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED
EXPECTED_PAGES = 8
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
    "r068_centered_form": (
        CLAIM_DIR / "classii_tip_safe_grouped_harvest_carleson_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-23-integrated-tip-safe-grouped-harvest-carleson-reduction/result.json",
    ),
    "r071_one_form": (
        CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-one-form-sobolev-linear-closure/result.json",
    ),
    "r078_hessian_packet": (
        CLAIM_DIR / "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-hessian-difference-safe-packet-doob-bracket/result.json",
    ),
    "r085_boundary": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-086", RESULT_ID, "translated-Wick", "coefficient-dominant")),
    "roadmap": (REPO / "ROADMAP.md", ("R-086", "translated-Wick", "coefficient-dominant", "Sector A remains open")),
    "gates": (REPO / "claims/GATES.md", ("R-086", "coefficient-dominant", "mixed production atom")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "13/15", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-086", RESULT_ID, "translated-Wick", "coefficient-dominant")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-086", "translated-Wick", "13/15")),
    "todo": (REPO / "todo/todo.json", ("R-086", "coefficient-dominant", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-086", "coefficient-dominant", "mixed production atom")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-086", "translated-Wick", "coefficient-dominant")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-086", "13/15", "high--high-to-low")),
    "sector": (REPO / "theory/sectors/A.md", ("RATIONAL-TRANSLATED-WICK-SEPARATION-AND-HEAT-SCHUR",)),
    "negative_registry": (REPO / "negative-results/registry.md", ("NG-2026-07-25-A13-RATIONAL-TRANSLATED-WICK-SEPARATION-AND-HEAT-SCHUR", "method no-go")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000121", "EXP-000125", "R-086")),
    "changelog": (REPO / "CHANGELOG.md", ("R-086", "translated-Wick")),
}

NOTE_TOKENS = (
    "Exact translated-Wick normal form",
    "Theorem 4.1",
    "A sharp cubic Sobolev payment",
    "Theorem 5.1",
    "The single surviving coefficient-dominant packet",
    "Exact inseparability diagnostics",
    "NG-2026-07-25-A13-RATIONAL-TRANSLATED-WICK-",
    "Proof-and-failure map",
    "No-overclaim statement",
)

PDF_TOKENS = (
    "translated-Wick normal form",
    "sharp cubic Sobolev payment",
    "Dyadic closure",
    "coefficient-dominant packet",
    "inseparability diagnostics",
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
    return subprocess.run([sys.executable, str(path)], cwd=REPO, capture_output=True, text=True, timeout=CHILD_TIMEOUT_SECONDS, check=False)


def record_passes(record: dict[str, Any]) -> bool:
    rows = record.get("assertions")
    return record.get("status") == "PASS" and isinstance(rows, list) and bool(rows) and all(isinstance(row, dict) and row.get("status") == "PASS" for row in rows)


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def authority_passes(record: dict[str, Any]) -> bool:
    assertion_rows = record.get("assertions") or record.get("integrated_assertions") or record.get("cross_assertions")
    verdict = record.get("status") == "PASS" or record.get("pass") is True or "PASS" in str(record.get("verdict", ""))
    return verdict and isinstance(assertion_rows, list) and bool(assertion_rows) and all(row.get("status") == "PASS" for row in assertion_rows)


def main() -> int:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    try:
        manifest = load_json(MANIFEST)
    except Exception as exc:
        manifest = {}
        failures.append(f"manifest: {exc}")

    child_specs = (
        ("primary", PRIMARY, PRIMARY_OUTPUT, f"[R-086 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, f"[R-086 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
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
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-rational-translated-wick-payload-comparable-reduction-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-rational-translated-wick-payload-comparable-reduction-independent/1.0", independent.get("schema"), "independent/1.0")

    try:
        normal_residual = float(independent["normal_form_max_residual"])
    except Exception:
        normal_residual = float("inf")
    add(rows, "cross_normal_form", normal_residual < 1e-50, normal_residual, "<1e-50")
    for key, expected in (("x", "11/20"), ("y", "19/60"), ("total", "13/15"), ("slack", "2/15"), ("moment", "15/2")):
        primary_value = primary.get("payable_ledgers", {}).get("base_frozen_cubic_q", {}).get(key)
        independent_value = independent.get("cubic_ledger", {}).get(key)
        add(rows, f"cross_cubic_{key}", primary_value == independent_value == expected, [primary_value, independent_value], expected)
    try:
        l21_delta = abs(float(primary["fixtures"]["kernel_l21_production"]) - float(independent["kernel_l21_production"]))
    except Exception:
        l21_delta = float("inf")
    add(rows, "cross_kernel_l21", l21_delta < 1e-14, l21_delta, "<1e-14")
    try:
        heat_delta = abs(float(primary["fixtures"]["heat_leading_coefficient"]) - float(independent["heat"]["predicted_coefficient"]))
    except Exception:
        heat_delta = float("inf")
    add(rows, "cross_heat_coefficient", heat_delta < 1e-14, heat_delta, "<1e-14")
    add(rows, "primary_q_total", primary.get("payable_ledgers", {}).get("payload_comparable_q", {}).get("total") == "7/10", primary.get("payable_ledgers", {}).get("payload_comparable_q"), "7/10")
    add(rows, "primary_g_total", primary.get("payable_ledgers", {}).get("payload_comparable_g", {}).get("total") == "23/30", primary.get("payable_ledgers", {}).get("payload_comparable_g"), "23/30")
    add(rows, "primary_remaining_target", "coefficient-dominant" in str(primary.get("remaining_rational_target")), primary.get("remaining_rational_target"), "coefficient-dominant")

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
    add(rows, "note_no_literal_qquad", "qquad" not in note_text.replace("\\qquad", ""), "literal qquad absent", "absent")
    add(rows, "note_honesty_boundary", all(token in note_text for token in ("No coefficient-dominant rational packet bound", "production Cartan", "Sector-A closure")), "open boundaries present", "present")

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
        surface_text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(rows, f"surface_{label}_tokens", all(token in surface_text for token in tokens), [token for token in tokens if token not in surface_text], [])

    claims_not = manifest.get("claims_not_established", {})
    required_false = (
        "coefficient_dominant_rational_packet", "rational_shifted_hessian_form_bound", "complete_rational_near",
        "production_cartan_atom_estimate", "controlled_cartan_cfar", "complete_signed_near",
        "complete_regular_packet_lower_bound", "overlap_uniform_bound", "full_progressive_revisit_extension",
        "controlled_shell_one_use", "nelson_bound", "interacting_measure", "sector_a_closure", "tier_promotion",
    )
    add(rows, "manifest_open_flags_false", all(claims_not.get(key) is False for key in required_false), {key: claims_not.get(key) for key in required_false}, "all false")
    consequence = manifest.get("consequence", {})
    add(rows, "manifest_normal_form_true", consequence.get("translated_wick_normal_form") is True, consequence.get("translated_wick_normal_form"), True)
    add(rows, "manifest_payable_branches_true", consequence.get("rational_nonresonant_payload_comparable_paid") is True, consequence.get("rational_nonresonant_payload_comparable_paid"), True)
    add(rows, "manifest_negative_registered", "NG-2026-07-25-A13-RATIONAL-TRANSLATED-WICK-SEPARATION-AND-HEAT-SCHUR" in manifest.get("negative_results", []), manifest.get("negative_results"), "contains R-086 no-go")
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
        "schema": "tect/a13-rational-translated-wick-payload-comparable-reduction-integrated/1.0",
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) and not failures else "FAIL",
        "pass": passed == len(rows) and not failures,
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "aggregate_assertions": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows),
        "assertions": rows,
        "failures": failures,
        "cross_summary": {"primary": EXPECTED_PRIMARY, "independent": EXPECTED_INDEPENDENT, "integrated": len(rows), "aggregate": EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + len(rows)},
        "proved_scope": "manifest-pinned R-086 translated-Wick normal form, cubic payment, and nonresonant/payload-comparable rational reduction",
        "open_scope": "coefficient-dominant rational packet, complete rational NEAR, Cartan atom, REG, OVERLAP, CORE, one-use, Nelson, measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-086 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-086 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
