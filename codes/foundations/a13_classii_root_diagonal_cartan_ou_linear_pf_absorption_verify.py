#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-084 A13 package."""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_root_diagonal_cartan_ou_linear_pf_absorption.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_root_diagonal_cartan_ou_linear_pf_absorption_independent.py"
MANIFEST = CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-root-diagonal-cartan-ou-linear-pauli-fierz-absorption-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-root-diagonal-cartan-ou-linear-pf-absorption/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-root-diagonal-cartan-ou-linear-pf-absorption/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json"
EXPECTED_PRIMARY = 50
EXPECTED_INDEPENDENT = 40
# Package contract oracles. The `+ 1` check below counts its own final row and
# therefore fails closed if an assertion is added or removed without a manifest
# and contract review.
EXPECTED_INTEGRATED = 131
EXPECTED_AGGREGATE = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED
EXPECTED_PAGES = 10
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "a1_production": (
        REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
        None,
    ),
    "r050_geometric_current": (
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/classii_k_composite_manifest.json",
        REPO / "claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-07-20-integrated-k-composite/result.json",
    ),
    "r063_balanced_jet": (
        CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
    ),
    "r071_one_form": (
        CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-one-form-sobolev-linear-closure/result.json",
    ),
    "r079_full_current": (
        CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json",
    ),
    "r083_cartan_linear_forest": (
        CLAIM_DIR / "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-controlled-polynomial-cfar-linear-pf-forest/result.json",
    ),
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-084", RESULT_ID, "OU-gradient", "linear Pauli--Fierz")),
    "roadmap": (REPO / "ROADMAP.md", ("R-084", "root-diagonal", "rational", "Sector A remains open")),
    "gates": (REPO / "claims/GATES.md", ("R-084", "far-projected OU-gradient", "linear Pauli--Fierz")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "50/50", "40/40", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-084", RESULT_ID, "root-diagonal", "linear")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-084", "OU", "rational")),
    "todo": (REPO / "todo/todo.json", ("R-084", "far-projected OU-gradient", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-084", "OU-gradient", "rational")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-084", "root-diagonal", "linear Pauli--Fierz")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-084", "OU", "linear")),
    "sector": (REPO / "theory/sectors/A.md", ("R-084", "ROOT-ORTHOGONALITY-ONE-USE")),
    "negative_registry": (REPO / "negative-results/registry.md", ("NG-2026-07-25-A13-ROOT-ORTHOGONALITY-ONE-USE", "production spatial paracomposition")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000107", "EXP-000112", "R-084")),
    "changelog": (REPO / "CHANGELOG.md", ("R-084", "root-diagonal Cartan OU")),
}

NOTE_TOKENS = (
    "Theorem 3.1 (exact root-first CFAR identity)",
    "Theorem 4.1 (conditional OU-resolvent identity)",
    "Root orthogonality alone is not one-use",
    "NG-2026-07-25-A13-ROOT-ORTHOGONALITY-ONE-USE",
    "Theorem 6.1 (complete heat-lifted linear endpoint)",
    "Theorem 7.1 (linear Pauli--Fierz NEAR absorption)",
    "Sharp linear floor and the R-083 fixture",
    "No-overclaim statement",
)

PDF_TOKENS = (
    "root-first CFAR identity",
    "conditional OU-resolvent identity",
    "Root orthogonality alone is not one-use",
    "complete heat-lifted linear endpoint",
    "linear Pauli",
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


def row_group(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        value = record.get(key)
        if isinstance(value, list) and value:
            return value
    return None


def record_passes(record: dict[str, Any]) -> bool:
    if record.get("failures") or record.get("failure_stage") is not None:
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

    child_specs = (
        ("primary", PRIMARY, PRIMARY_OUTPUT, f"[R-084 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, f"[R-084 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
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
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-primary/1.0", primary.get("schema"), "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-independent/1.0", independent.get("schema"), "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-independent/1.0")

    for key in ("P", "alpha", "c0", "c1", "cS", "cartan_prefactor", "horizontal_sharp_floor", "linear_full_sharp_floor"):
        try:
            delta = abs(Decimal(str(primary["derived_constants"][key])) - Decimal(str(independent["derived_constants"][key])))
        except Exception:
            delta = Decimal("Infinity")
        add(rows, f"cross_constant_{key}", delta < Decimal("1e-14"), str(delta), "<1e-14")
    for key in ("old_input_energy", "equal_input_energy", "operator_norm_squared"):
        try:
            delta = abs(float(primary["root_tree"][key]) - float(independent["root_tree"][key]))
        except Exception:
            delta = float("inf")
        add(rows, f"cross_tree_{key}", delta < 1e-12, delta, "<1e-12")
    for key in ("UQ_total", "centered_Q_total", "current_totals", "worst_required_moment"):
        add(rows, f"cross_ledger_{key}", primary.get("young_ledger", {}).get(key) == independent.get("young_ledger", {}).get(key), [primary.get("young_ledger", {}).get(key), independent.get("young_ledger", {}).get(key)], "equal")
    for key, tolerance in (("E_A2_over_lambda2", 1e-9), ("E_A6_over_lambda6", 1e-5), ("packet_quadratic_coefficient", 1e-12)):
        try:
            delta = abs(float(primary["fixture"][key]) - float(independent["fixture"][key]))
        except Exception:
            delta = float("inf")
        add(rows, f"cross_fixture_{key}", delta < tolerance, delta, f"<{tolerance}")

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
            add(rows, f"{label}_result_passes", record_passes(authority_record), authority_record.get("status", authority_record.get("verdict")), "PASS")

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
    add(rows, "note_honesty_boundary", all(token in note_text for token in ("rational Pauli--Fierz row remains open", "controlled-shell one-use", "Sector-A closure")), "open boundaries present", "present")

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
        "complete_controlled_CFar", "complete_regular_packet_lower_bound", "complete_signed_NEAR",
        "controlled_Cartan_CFar", "controlled_shell_one_use", "full_progressive_revisit_extension",
        "interacting_measure", "nelson_bound", "sector_a_closure", "tier_promotion",
    )
    add(rows, "manifest_open_flags_false", all(claims_not.get(key) is False for key in required_false), {key: claims_not.get(key) for key in required_false}, "all false")
    add(rows, "manifest_linear_subbranch_true", manifest.get("consequence", {}).get("linear_pauli_fierz_NEAR_regular_one_shot") is True, manifest.get("consequence", {}).get("linear_pauli_fierz_NEAR_regular_one_shot"), True)
    add(rows, "manifest_negative_registered", "NG-2026-07-25-A13-ROOT-ORTHOGONALITY-ONE-USE" in manifest.get("negative_results", []), manifest.get("negative_results"), "contains new no-go")
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
        "schema": "tect/a13-root-diagonal-cartan-ou-linear-pf-absorption-integrated/1.0",
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
        "proved_scope": "manifest-pinned R-084 root-diagonal Cartan OU reduction and regular one-shot linear Pauli--Fierz NEAR absorption",
        "open_scope": "production Cartan OU-gradient estimate, rational/complete NEAR, progression, one-use, Nelson, measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-084 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-084 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
