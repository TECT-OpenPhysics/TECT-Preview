#!/usr/bin/env python3
"""Fail-closed integrated verifier for the R-087 A13 package."""

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
RESULT_ID = "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_cartan_spatial_decay_rational_trace_variational_core_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_cartan_spatial_decay_rational_trace_variational_core_reduction_independent.py"
MANIFEST = CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json"
EXPECTED_PRIMARY = 49
EXPECTED_INDEPENDENT = 53
EXPECTED_INTEGRATED = 132
EXPECTED_AGGREGATE = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED
EXPECTED_PAGES = 9
CHILD_TIMEOUT_SECONDS = 120


AUTHORITY = {
    "r075_graph": (
        CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
        CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
    ),
    "r081_cartan_tail": (
        CLAIM_DIR / "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-tail-adapted-near-temporal-reduction/result.json",
    ),
    "r084_root_diagonal": (
        CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-root-diagonal-cartan-ou-linear-pf-absorption/result.json",
    ),
    "r085_boundary": (
        CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-nonorthogonal-cartan-schur-rational-hessian-boundary/result.json",
    ),
    "r086_rational": (
        CLAIM_DIR / "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-rational-translated-wick-payload-comparable-reduction/result.json",
    ),
}


SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-087", RESULT_ID, "7/30", "variational CORE")),
    "roadmap": (REPO / "ROADMAP.md", ("R-087", "Cartan one-use", "OVERLAP", "Sector A remains open")),
    "gates": (REPO / "claims/GATES.md", ("R-087", "variational CORE", "Cartan one-use")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "7/12", "Sector A remains open")),
    "claim": (CLAIM_DIR / "claim.md", ("R-087", RESULT_ID, "trace debt")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-087", "Cartan spatial", "variational CORE")),
    "todo": (REPO / "todo/todo.json", ("R-087", "Cartan one-use", "Sector A remains open")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-087", "Cartan one-use", "OVERLAP")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-087", "7/12", "variational CORE")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-087", "trace debt", "OVERLAP")),
    "sector": (REPO / "theory/sectors/A.md", ("PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION",)),
    "negative_registry": (REPO / "negative-results/registry.md", ("NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION", "method no-go")),
    "explorations": (REPO / "explorations/log.jsonl", ("EXP-000126", "EXP-000129", "EXP-000130", "R-087")),
    "changelog": (REPO / "CHANGELOG.md", ("R-087", "Cartan spatial")),
}


NOTE_TOKENS = (
    "A reproduced order-two paralinearisation lemma",
    "Exact principal support and the safe separation",
    "Theorem 5.1",
    "The exact Cartan one-use obstruction",
    "Exact rational eta-completion and trace debt",
    "Theorem 8.1",
    "Bailleul and F. Bernicot",
    "Y. Hariya and S. Watanabe",
    "NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION",
    "Proof-and-failure map",
    "No-overclaim statement",
)


PDF_TOKENS = (
    "Cartan spatial decay",
    "order-two paralinearisation",
    "safe separation",
    "Hilbert–Schmidt decay",
    "Cartan one-use obstruction",
    "rational eta-completion",
    "variational CORE",
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
        ("primary", PRIMARY, PRIMARY_OUTPUT, f"[R-087 primary] {EXPECTED_PRIMARY}/{EXPECTED_PRIMARY} PASS", EXPECTED_PRIMARY),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT, f"[R-087 independent] {EXPECTED_INDEPENDENT}/{EXPECTED_INDEPENDENT} PASS", EXPECTED_INDEPENDENT),
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
    add(rows, "primary_schema", primary.get("schema") == "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-primary/1.0", primary.get("schema"), "primary/1.0")
    add(rows, "independent_schema", independent.get("schema") == "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-independent/1.0", independent.get("schema"), "independent/1.0")

    cross_specs = (
        ("cartan", "beta", "7/5"),
        ("cartan", "maximum_s", "7/10"),
        ("cartan", "root_margin", "7/30"),
        ("cartan", "gap_margin", "13/30"),
        ("variational_core", "q", "10/9"),
        ("variational_core", "energy_coefficient", "9/20"),
        ("variational_core", "q_minus_p", "1/90"),
        ("variational_core", "energy_reserve", "1/220"),
    )
    for section, key, expected in cross_specs:
        p_value = primary.get(section, {}).get(key)
        i_value = independent.get(section, {}).get(key)
        add(rows, f"cross_{section}_{key}", p_value == i_value == expected, [p_value, i_value], expected)
    try:
        cartan_fft_residual = float(independent.get("cartan", {}).get("two_mode_max_residual", float("inf")))
        rational_residual = float(independent.get("rational", {}).get("random_max_residual", float("inf")))
    except Exception:
        cartan_fft_residual = rational_residual = float("inf")
    add(rows, "cross_cartan_fft_residual", cartan_fft_residual < 2e-8, cartan_fft_residual, "<2e-8")
    add(rows, "cross_rational_random_residual", rational_residual < 2e-12, rational_residual, "<2e-12")
    add(rows, "primary_safe_C0", primary.get("cartan", {}).get("safe_C0") == 5, primary.get("cartan", {}).get("safe_C0"), 5)
    add(rows, "independent_safe_C0", independent.get("cartan", {}).get("safe_C0") == 5, independent.get("cartan", {}).get("safe_C0"), 5)

    add(rows, "manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_t4_open", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(rows, f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(rows, f"{label}_manifest_hash", authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest), pin.get("manifest", {}).get("sha256"), None if not authority_manifest.exists() else digest(authority_manifest))
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
    add(rows, "note_smooth_lp_boundary", all(token in note_text for token in ("smooth analytic LP", "C_0=5", "sharp partial-sum kernels")), "declared smooth convention", "present")
    add(rows, "note_honesty_boundary", all(token in note_text for token in ("1/3<alpha<1/2", "local polynomial envelope", "one-use ledger", "coefficient-dominant", "Sector-A closure")), "qualified range, exact payoff hypothesis, and open boundaries present", "present")

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
        "cartan_one_use_q_ledger", "complete_production_cartan_atom_estimate", "controlled_cartan_cfar",
        "coefficient_dominant_rational_packet", "rational_shifted_hessian_form_bound", "complete_rational_near",
        "complete_signed_near", "complete_regular_packet_lower_bound", "overlap_uniform_bound",
        "controlled_shell_one_use", "nelson_bound", "interacting_measure", "sector_a_closure", "tier_promotion",
    )
    add(rows, "manifest_open_flags_false", all(claims_not.get(key) is False for key in required_false), {key: claims_not.get(key) for key in required_false}, "all false")
    consequence = manifest.get("consequence", {})
    add(rows, "manifest_cartan_spatial_true", consequence.get("cartan_spatial_atom_decay") is True and str(consequence.get("cartan_s_range", "")).startswith("1/3<alpha<1/2"), {"proved": consequence.get("cartan_spatial_atom_decay"), "range": consequence.get("cartan_s_range")}, "proved with qualified range")
    add(rows, "manifest_rational_completion_true", consequence.get("rational_eta_completion") is True, consequence.get("rational_eta_completion"), True)
    add(rows, "manifest_variational_core_true", consequence.get("fixed_cutoff_variational_core") is True, consequence.get("fixed_cutoff_variational_core"), True)
    add(rows, "manifest_cartan_ledger_false", consequence.get("cartan_one_use_q_ledger") is False, consequence.get("cartan_one_use_q_ledger"), False)
    add(rows, "manifest_negative_registered", "NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION" in manifest.get("negative_results", []), manifest.get("negative_results"), "contains R-087 no-go")
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
        "schema": "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-integrated/1.0",
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
        "proved_scope": "manifest-pinned R-087 Cartan spatial atom decay, rational eta/trace reduction, and fixed-cutoff bounded cylindrical variational core",
        "open_scope": "Cartan one-use q-ledger, complete Cartan CFAR, coefficient-dominant rational packet, rational/signed NEAR, REG, OVERLAP, Nelson, measure, and Sector A",
    }
    atomic_json(OUTPUT, payload)
    if payload["pass"]:
        print(f"[R-087 integrated] {passed}/{len(rows)} PASS; aggregate={payload['aggregate_assertions']}/{payload['aggregate_assertions']}")
        return 0
    failed_names = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-087 integrated] {passed}/{len(rows)} PASS; failed={failed_names}; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
