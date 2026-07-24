#!/usr/bin/env python3
"""Fail-closed integrated verifier for R-079."""

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
RESULT_ID = "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_full_safe_packet_frame_current_doob.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_full_safe_packet_frame_current_doob_independent.py"
MANIFEST = CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json"
NOTE = CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-full-safe-packet-frame-current-doob/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-full-safe-packet-frame-current-doob/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-integrated-full-safe-packet-frame-current-doob/result.json"
EXPECTED_PRIMARY = 51
EXPECTED_INDEPENDENT = 42
EXPECTED_INTEGRATED = 157
CHILD_TIMEOUT_SECONDS = 120

AUTHORITY = {
    "r063_balanced_jet": {
        "manifest": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-22-integrated-balanced-coefficient-jet-continuum/result.json",
        "schema": "tect/a13-balanced-coefficient-jet-continuum-integrated-result/1.0",
        "result_id": "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION",
        "rows": 48,
        "aggregate": 109,
    },
    "r066_backward_heat": {
        "manifest": CLAIM_DIR / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json",
        "schema": "tect/a13-backward-heat-martingale-square-coupled-cartan-integrated-result/1.0",
        "result_id": "A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION",
        "rows": 65,
        "aggregate": 103,
    },
    "r070_wick_doob": {
        "manifest": CLAIM_DIR / "classii_wick_doob_terminal_resolvent_reduction_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-24-integrated-wick-doob-terminal-resolvent-reduction/result.json",
        "schema": "tect/a13-wick-doob-terminal-resolvent-integrated/1.0",
        "result_id": "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION",
        "rows": 47,
        "aggregate": 85,
    },
    "r073_off_diagonal": {
        "manifest": CLAIM_DIR / "classii_off_diagonal_telescope_critical_phase_root_reduction_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-24-integrated-off-diagonal-telescope-critical-phase-root-reduction/result.json",
        "schema": "tect/a13-off-diagonal-telescope-critical-phase-root-integrated/1.0",
        "result_id": "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-REDUCTION",
        "rows": 51,
        "aggregate": 113,
    },
    "r077_causal_packet": {
        "manifest": CLAIM_DIR / "classii_causal_packet_payload_resonance_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-25-integrated-causal-packet-payload-resonance/result.json",
        "schema": "tect/a13-causal-packet-payload-integrated/1.0",
        "result_id": "A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION",
        "rows": 110,
        "aggregate": 171,
    },
    "r078_hessian_safe_packet": {
        "manifest": CLAIM_DIR / "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
        "result": CLAIM_DIR / "runs/2026-07-25-integrated-hessian-difference-safe-packet-doob-bracket/result.json",
        "schema": "tect/a13-hessian-safe-packet-doob-integrated/1.0",
        "result_id": "A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION",
        "rows": 176,
        "aggregate": 233,
    },
}

SURFACES = {
    "results": (REPO / "RESULTS-LEDGER.md", ("R-079", RESULT_ID)),
    "negative": (
        REPO / "negative-results/registry.md",
        (
            "NG-2026-07-25-A13-GENERIC-WEIGHTED-DOOB-SHORTCUTS",
            "NG-2026-07-25-A13-ADAPTED-WICK-CARRE-DU-CHAMP",
        ),
    ),
    "roadmap": (REPO / "ROADMAP.md", ("R-079", "production near/far")),
    "gates": (REPO / "claims/GATES.md", ("R-079", "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET")),
    "status": (CLAIM_DIR / "status.json", (RESULT_ID, "near/far")),
    "lineage": (CLAIM_DIR / "lineage-narrative.md", ("R-079", "weighted Cameron")),
    "todo": (REPO / "todo/todo.json", ("R-079", "near/far")),
    "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-079", "near/far")),
    "main_line": (REPO / "theory/main-proof-line.md", ("R-079", "near/far")),
    "foundation": (REPO / "theory/sector-A-foundation/README.md", ("R-079", "near/far")),
}

NOTE_TOKENS = (
    "Theorem 3.1 (full-current identity)",
    "Exact reconstruction of the canonical safe packet",
    "Spatially weighted Cameron--Martin square function",
    "Adapted Wick--carr\\'e-du-champ no-go",
    "structural fixtures",
    "production weighted packet lower bound",
)
PDF_TOKENS = (
    "Full safe-packet frame-current Doob decomposition",
    "full-current identity",
    "weighted Cameron",
    "generic weighted shortcuts fail",
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
    rows.append(
        {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected}
    )


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
        relative_label = path.relative_to(REPO).as_posix().replace("/", "__")
        add(rows, f"exists_{relative_label}", path.exists(), path.exists(), True)
    if not all(path.exists() for path in required):
        print("[R-079 integrated] FAIL -- missing required files")
        return 1

    manifest = load_json(MANIFEST)
    primary_process = run_child(PRIMARY)
    independent_process = run_child(INDEPENDENT)
    add(rows, "primary_exit_zero", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "independent_exit_zero", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "primary_sentinel", "51/51 PASS" in primary_process.stdout, primary_process.stdout.strip(), "contains 51/51 PASS")
    add(rows, "independent_sentinel", "42/42 PASS" in independent_process.stdout, independent_process.stdout.strip(), "contains 42/42 PASS")
    add(rows, "primary_output_exists", PRIMARY_OUTPUT.exists(), PRIMARY_OUTPUT.exists(), True)
    add(rows, "independent_output_exists", INDEPENDENT_OUTPUT.exists(), INDEPENDENT_OUTPUT.exists(), True)
    if not PRIMARY_OUTPUT.exists() or not INDEPENDENT_OUTPUT.exists():
        return 1

    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = (
        ("primary", primary, EXPECTED_PRIMARY, "tect/a13-full-safe-packet-frame-current-doob-primary/1.0"),
        ("independent", independent, EXPECTED_INDEPENDENT, "tect/a13-full-safe-packet-frame-current-doob-independent/1.0"),
    )
    for label, record, expected, schema in children:
        add(rows, f"{label}_schema", record.get("schema") == schema, record.get("schema"), schema)
        add(rows, f"{label}_result", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(rows, f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(rows, f"{label}_version", record.get("source_version") == "1.0.0", record.get("source_version"), "1.0.0")
        add(rows, f"{label}_status", record.get("status") == "PASS", record.get("status"), "PASS")
        add(rows, f"{label}_passed", record.get("assertions_passed") == expected, record.get("assertions_passed"), expected)
        add(rows, f"{label}_total", record.get("assertions_total") == expected, record.get("assertions_total"), expected)
        child_rows = record.get("assertions", [])
        add(rows, f"{label}_row_count", len(child_rows) == expected, len(child_rows), expected)
        add(rows, f"{label}_rowwise_pass", all(row.get("status") == "PASS" for row in child_rows), sum(row.get("status") == "PASS" for row in child_rows), expected)
        no_claims = record.get("claims_not_established", {})
        add(rows, f"{label}_no_overclaim", bool(no_claims) and all(value is False for value in no_claims.values()), no_claims, "all false")
        scope = record.get("safe_subtractor_fixture_scope", "")
        add(rows, f"{label}_paid_fixture_scope", "structural" in scope and "not" in scope.lower(), scope, "structural-only boundary")

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    forbidden = re.search(r"(?:from|import)\s+a13_classii_full_safe_packet_frame_current_doob(?:\s|$)", independent_source)
    add(rows, "independent_non_importing", forbidden is None and independent.get("imports_primary") is False, {"source_import": bool(forbidden), "reported": independent.get("imports_primary")}, {"source_import": False, "reported": False})

    primary_exp = primary.get("exponents", {})
    independent_exp = independent.get("exponents", {})
    exact_pairs = {
        "combined_x": (primary_exp.get("combined_x"), independent_exp.get("combined_x"), "9/10"),
        "combined_y": (primary_exp.get("combined_y"), independent_exp.get("combined_y"), "11/30"),
        "deficit": (primary_exp.get("combined_slack"), independent_exp.get("deficit"), "-4/15"),
    }
    for label, (left, right, expected) in exact_pairs.items():
        add(rows, f"cross_{label}", left == right == expected, (left, right), expected)
    gain_primary = primary.get("conditional_positive_gain_ledger", {})
    gain_expected = {
        "x_power": "17/40", "y_power": "21/40", "slack": "1/20",
        "random_moment": "20", "eta_loss": "17/2", "zeta_loss": "21/2",
    }
    independent_gain_keys = {
        "x_power": "gain_x", "y_power": "gain_y", "slack": "gain_slack",
        "random_moment": "gain_moment", "eta_loss": "gain_eta", "zeta_loss": "gain_zeta",
    }
    for key, expected in gain_expected.items():
        actual = (gain_primary.get(key), independent_exp.get(independent_gain_keys[key]))
        add(rows, f"cross_gain_{key}", actual[0] == actual[1] == expected, actual, expected)

    current = primary.get("full_current_decomposition", {})
    for key in (
        "energy_identity_error", "safe_telescope_error", "complete_endpoint_error",
        "increment_reassembly_error", "commutator_error", "trace_split_error",
        "predictability_error", "past_increment_error", "joined_causal_decomposition_error",
        "joined_endpoint_safe_error",
    ):
        add(rows, f"primary_current_{key}", abs(float(current.get(key, 1.0))) < 1.0e-12, current.get(key), 0.0)
    add(rows, "primary_cross_retained", abs(float(current.get("cross_sum", 0.0))) > 1.0e-10, current.get("cross_sum"), "nonzero")
    add(rows, "primary_paid_nonzero", abs(float(current.get("paid_difference", 0.0))) > 1.0e-10, current.get("paid_difference"), "nonzero")

    matrix = independent.get("matrix_decomposition", {})
    for key in (
        "energy_error", "telescope_error", "reassembly_error", "commutator_error",
        "trace_split_error", "predictability_error", "past_increment_error",
        "joined_causal_decomposition_error", "joined_endpoint_safe_error",
        "metric_convention_error", "covariance_convention_error",
    ):
        add(rows, f"independent_matrix_{key}", abs(float(matrix.get(key, 1.0))) < 1.0e-11, matrix.get(key), 0.0)
    add(rows, "independent_cross_retained", abs(float(matrix.get("cross_sum", 0.0))) > 1.0e-10, matrix.get("cross_sum"), "nonzero")

    wick = primary.get("adapted_wick_no_go", {})
    wick_expected = {
        "normalized_remainder": "-2", "normalized_square": "7/2",
        "normalized_trace": "-11/2", "normalized_innovation_energy": "2",
    }
    for key, expected in wick_expected.items():
        add(rows, f"wick_{key}", wick.get(key) == expected, wick.get(key), expected)
    add(rows, "bounded_wick_negative", float(wick.get("exponential_remainder", 1.0)) < 0.0, wick.get("exponential_remainder"), "<0")
    weighted = primary.get("weighted_cm_square_function", {})
    add(rows, "weighted_cm_one_use", float(weighted.get("margin", -1.0)) >= -1.0e-12 and float(weighted.get("weighted_square", 0.0)) > 0.0, weighted, "nonzero and within energy")
    spatial = primary.get("generic_spatial_no_go", {})
    add(rows, "spatial_scaling", float(spatial.get("scaling_error", 1.0)) < 1.0e-11 and float(spatial.get("weighted_y_norm_spread", 1.0)) < 1.0e-12, spatial, "N^s bracket with constant H^-s norm")
    rare = independent.get("weighted_cm_and_bmo", {})
    add(rows, "rare_expected_budgets", abs(float(rare.get("rare_energy", 0.0)) - 1.0) < 1.0e-12 and abs(float(rare.get("rare_sextic", 0.0)) - 1.0) < 1.0e-12, rare, "energy=sextic=1")
    add(rows, "rare_conditional_growth", float(rare.get("rare_conditional", 0.0)) > 700.0, rare.get("rare_conditional"), ">700")

    for key, contract in AUTHORITY.items():
        manifest_entry = manifest.get("authority", {}).get(key, {})
        result_entry = manifest.get("authority_results", {}).get(key, {})
        for label, path, entry in (("manifest", contract["manifest"], manifest_entry), ("result", contract["result"], result_entry)):
            relative = path.relative_to(REPO).as_posix()
            add(rows, f"authority_{key}_{label}_path", entry.get("path") == relative, entry.get("path"), relative)
            add(rows, f"authority_{key}_{label}_hash", entry.get("sha256") == digest(path), entry.get("sha256"), digest(path))
        record = load_json(contract["result"])
        group = row_group(record) or []
        actual_contract = {
            "schema": record.get("schema"), "result_id": record.get("result_id"),
            "rows": len(group), "aggregate": aggregate_count(record), "pass": record_passes(record),
        }
        expected_contract = {
            "schema": contract["schema"], "result_id": contract["result_id"],
            "rows": contract["rows"], "aggregate": contract["aggregate"], "pass": True,
        }
        add(rows, f"authority_{key}_contract", actual_contract == expected_contract, actual_contract, expected_contract)

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
    add(rows, "pdf_pages", len(reader.pages) == 10 and pdf_entry.get("pages") == 10, {"actual": len(reader.pages), "manifest": pdf_entry.get("pages")}, 10)
    add(rows, "pdf_size", PDF.stat().st_size > 100_000 and pdf_entry.get("size_bytes") == PDF.stat().st_size, {"actual": PDF.stat().st_size, "manifest": pdf_entry.get("size_bytes")}, ">100000 and exact")
    add(rows, "pdf_forms", not fields and pdf_entry.get("form_check") == "PASS", {"fields": len(fields), "manifest": pdf_entry.get("form_check")}, {"fields": 0, "manifest": "PASS"})
    pdf_text = normalized_pdf_text(PDF)
    add(rows, "pdf_tokens", all(token in pdf_text for token in PDF_TOKENS), {token: token in pdf_text for token in PDF_TOKENS}, "all true")
    add(rows, "pdf_no_debris", all(token not in pdf_text.lower() for token in ("qquad", "undefined", "overfull")), {token: token in pdf_text.lower() for token in ("qquad", "undefined", "overfull")}, "all false")
    add(rows, "pdf_visual_qa", pdf_entry.get("visual_qa") == "PASS" and "ten pages" in pdf_entry.get("visual_qa_note", "").lower(), pdf_entry.get("visual_qa_note"), "PASS and ten-page note")

    note_text = NOTE.read_text(encoding="utf-8")
    add(rows, "note_tokens", all(token in note_text for token in NOTE_TOKENS), {token: token in note_text for token in NOTE_TOKENS}, "all true")
    add(rows, "note_no_bare_qquad", re.search(r"(?<!\\)qquad", note_text) is None, bool(re.search(r"(?<!\\)qquad", note_text)), False)
    add(rows, "note_no_overfull_marker", "Overfull \\hbox" not in note_text, "Overfull \\hbox" in note_text, False)

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-classii-full-safe-packet-frame-current-doob-decomposition/1.0", manifest.get("schema"), "tect/a13-classii-full-safe-packet-frame-current-doob-decomposition/1.0")
    add(rows, "manifest_version", manifest.get("package_version") == __version__, manifest.get("package_version"), __version__)
    add(rows, "manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_t4_open", "T4" in manifest.get("status", "") and "OPEN" in manifest.get("status", ""), manifest.get("status"), "contains T4 and OPEN")
    no_established = manifest.get("claims_not_established", {})
    add(rows, "manifest_no_overclaim", bool(no_established) and all(value is False for value in no_established.values()), no_established, "all false")
    add(rows, "manifest_current_child", manifest.get("consequence", {}).get("current_child") == "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET", manifest.get("consequence", {}).get("current_child"), "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET")
    run_contract = manifest.get("run_contract", {})
    add(rows, "manifest_primary_count", run_contract.get("primary_assertions") == EXPECTED_PRIMARY, run_contract.get("primary_assertions"), EXPECTED_PRIMARY)
    add(rows, "manifest_independent_count", run_contract.get("independent_assertions") == EXPECTED_INDEPENDENT, run_contract.get("independent_assertions"), EXPECTED_INDEPENDENT)
    if EXPECTED_INTEGRATED:
        add(rows, "manifest_integrated_count", run_contract.get("integrated_assertions") == EXPECTED_INTEGRATED, run_contract.get("integrated_assertions"), EXPECTED_INTEGRATED)
        add(rows, "manifest_aggregate_count", run_contract.get("aggregate_assertions") == EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED, run_contract.get("aggregate_assertions"), EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + EXPECTED_INTEGRATED)

    for label, (path, tokens) in SURFACES.items():
        surface_text = path.read_text(encoding="utf-8") if path.exists() else ""
        add(rows, f"surface_{label}", path.exists() and all(token in surface_text for token in tokens), {"exists": path.exists(), **{token: token in surface_text for token in tokens}}, "exists and all true")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    aggregate = EXPECTED_PRIMARY + EXPECTED_INDEPENDENT + total
    payload = {
        "schema": "tect/a13-full-safe-packet-frame-current-doob-integrated/1.0",
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
        "source_sha256": digest(Path(__file__).resolve()),
    }
    atomic_json(OUTPUT, payload)
    if passed == total:
        print(f"[R-079 integrated] {passed}/{total} PASS; aggregate {aggregate}/{aggregate} PASS")
    else:
        print(f"[R-079 integrated] {passed}/{total} FAIL")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    print(f"result: {OUTPUT.relative_to(REPO).as_posix()}")
    exact_count = not EXPECTED_INTEGRATED or total == EXPECTED_INTEGRATED
    return 0 if passed == total and exact_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
