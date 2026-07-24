#!/usr/bin/env python3
"""Integrated verifier for R-076.

The verifier pins direct and predecessor authority hashes, executes the
primary and non-importing independent audits, cross-compares their derived
values, checks the proof-note/PDF contract, and enforces the T4 honesty
boundary.  It writes one reproducible integrated JSON artifact.
"""

from __future__ import annotations

__version__ = "1.0.3"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-25"

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-TRANSPORT-BESOV-BREGMAN-RESONANCE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_MANIFEST = CLAIM_DIR / "classii_signed_transport_besov_bregman_resonance_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-signed-transport-besov-bregman-resonance/result.json"

PRIMARY = REPO / "codes/foundations/a13_classii_signed_transport_besov_bregman_resonance.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_signed_transport_besov_bregman_resonance_independent.py"
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-24-primary-signed-transport-besov-bregman-resonance/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-independent-signed-transport-besov-bregman-resonance/result.json"

EXPECTED_PRIMARY_ASSERTIONS = 24
EXPECTED_INDEPENDENT_ASSERTIONS = 15
CHILD_TIMEOUT_SECONDS = 120


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def run_child(source: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(source)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=CHILD_TIMEOUT_SECONDS,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def integrated_pass(record: dict[str, Any]) -> bool:
    """Normalize issued predecessor schemas without accepting contradictions."""
    if "failures" in record:
        failures = record["failures"]
        if not isinstance(failures, list) or failures:
            return False
    if "failure_stage" in record and record["failure_stage"] is not None:
        return False

    row_group_seen = False
    for key in ("assertions", "cross_assertions", "integrated_assertions"):
        if key not in record:
            continue
        row_group_seen = True
        group = record[key]
        if not isinstance(group, list) or not group:
            return False
        if not all(isinstance(row, dict) and row.get("status") == "PASS" for row in group):
            return False
    if not row_group_seen:
        return False

    positive_signal = False
    summary = record.get("summary")
    if summary is not None:
        if not isinstance(summary, dict):
            return False
        if "verdict" in summary:
            if summary.get("verdict") != "PASS":
                return False
            positive_signal = True
        if any(key in summary for key in ("failed", "passed", "total")):
            if not (
                summary.get("failed") == 0
                and isinstance(summary.get("passed"), int)
                and summary.get("passed") == summary.get("total")
                and summary.get("total", 0) > 0
            ):
                return False
            positive_signal = True

    assertion_summary = record.get("assertion_summary")
    if assertion_summary is not None:
        if not isinstance(assertion_summary, dict):
            return False
        if not (
            isinstance(assertion_summary.get("integrated_total"), int)
            and assertion_summary.get("integrated_total", 0) > 0
            and assertion_summary.get("integrated_passed")
            == assertion_summary.get("integrated_total")
        ):
            return False
        positive_signal = True

    if "verdict" in record:
        verdict = record["verdict"]
        if not (verdict == "PASS" or (isinstance(verdict, str) and verdict.endswith("-PASS"))):
            return False
        positive_signal = True
    if "status" in record:
        if record["status"] != "PASS":
            return False
        positive_signal = True
    if "pass" in record:
        if record["pass"] is not True:
            return False
        positive_signal = True
    return positive_signal


def row_count(value: Any) -> int | None:
    if isinstance(value, (list, dict)):
        return len(value)
    return None


def predecessor_contract(record: dict[str, Any], authority: dict[str, Any]) -> dict[str, bool]:
    """Audit identity, links, failure signals, and issued count relationships."""
    claim_values = [record[key] for key in ("claim", "claim_id") if key in record]
    checks = {
        "pass": integrated_pass(record),
        "schema": record.get("schema") == authority["integrated_schema"],
        "claim": bool(claim_values) and all(value == authority["expected_claim"] for value in claim_values),
    }
    if "expected_result_id" in authority:
        checks["result_id"] = record.get("result_id") == authority["expected_result_id"]
    if "manifest_sha256" in record:
        checks["manifest_sha256"] = record["manifest_sha256"] == authority["sha256"]
    if "manifest" in record:
        checks["manifest_path"] = str(record["manifest"]).replace("\\", "/") == authority["path"]

    group = next(
        (record[key] for key in ("assertions", "cross_assertions", "integrated_assertions") if key in record),
        None,
    )
    integrated_count = row_count(group)
    if integrated_count is not None:
        if "assertion_count" in record:
            checks["assertion_count"] = record["assertion_count"] == integrated_count
        count_contract = record.get("count_contract")
        if isinstance(count_contract, dict) and "integrated" in count_contract:
            checks["count_contract_integrated"] = count_contract["integrated"] == integrated_count
            if all(key in count_contract for key in ("primary", "independent", "aggregate")):
                aggregate = count_contract["primary"] + count_contract["independent"] + count_contract["integrated"]
                checks["count_contract_aggregate_sum"] = count_contract["aggregate"] == aggregate
                checks["aggregate_assertion_count"] = record.get("aggregate_assertion_count") == aggregate
        assertion_summary = record.get("assertion_summary")
        if isinstance(assertion_summary, dict):
            checks["assertion_summary_total"] = assertion_summary.get("integrated_total") == integrated_count
            checks["assertion_summary_passed"] = assertion_summary.get("integrated_passed") == integrated_count
            if all(key in assertion_summary for key in ("primary_total", "independent_total", "aggregate_total")):
                checks["assertion_summary_aggregate_sum"] = assertion_summary["aggregate_total"] == (
                    assertion_summary["primary_total"]
                    + assertion_summary["independent_total"]
                    + assertion_summary["integrated_total"]
                )

        summary = record.get("summary")
        primary_count = row_count(record.get("primary", {}).get("assertions")) if isinstance(record.get("primary"), dict) else None
        independent_count = row_count(record.get("independent", {}).get("assertions")) if isinstance(record.get("independent"), dict) else None
        if isinstance(summary, dict) and primary_count is not None and independent_count is not None:
            checks["summary_aggregate_sum"] = summary.get("total") == primary_count + independent_count + integrated_count
    return checks


def child_contract(
    record: dict[str, Any],
    source: Path,
    manifest_hash: str,
    expected_schema: str,
    expected_version: str,
    expected_count: int,
) -> dict[str, bool]:
    rows = record.get("assertions")
    return {
        "schema": record.get("schema") == expected_schema,
        "result_id": record.get("result_id") == RESULT_ID,
        "claim": record.get("claim") == CLAIM,
        "source_version": record.get("source_version") == expected_version,
        "source_sha256": record.get("source_sha256") == digest(source),
        "manifest_sha256": record.get("manifest_sha256") == manifest_hash,
        "rows": isinstance(rows, list)
        and len(rows) == expected_count
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in rows),
        "summary": record.get("summary")
        == {"passed": expected_count, "total": expected_count, "verdict": "PASS"},
    }


def pdf_contract(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    pages = len(reader.pages)
    mediaboxes = [
        [float(page.mediabox.width), float(page.mediabox.height)]
        for page in reader.pages
    ]
    with pdfplumber.open(path) as document:
        text_pages = [(page.extract_text() or "") for page in document.pages]
    literal_debris = [
        {"page": page_number, "token": token}
        for page_number, text in enumerate(text_pages, start=1)
        for token in ("qquad", "qquaad")
        if token in text
    ]
    return {
        "pages": pages,
        "mediaboxes": mediaboxes,
        "all_pages_have_text": all(len(text.strip()) > 100 for text in text_pages),
        "first_page_text": text_pages[0][:500] if text_pages else "",
        "last_page_text": text_pages[-1][-900:] if text_pages else "",
        "total_text_characters": sum(len(text) for text in text_pages),
        "literal_control_debris": literal_debris,
    }


def run(manifest_path: Path = DEFAULT_MANIFEST, output_path: Path = DEFAULT_OUTPUT) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash = digest(manifest_path)
    rows: list[dict[str, Any]] = []

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-signed-transport-besov-bregman-resonance/1.0", manifest.get("schema"), "tect/a13-signed-transport-besov-bregman-resonance/1.0")
    add(rows, "manifest_result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add(rows, "manifest_claim", manifest.get("claim") == CLAIM, manifest.get("claim"), CLAIM)
    add(rows, "manifest_tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")
    add(rows, "manifest_ledger_id", manifest.get("result_ledger_id") == "R-076", manifest.get("result_ledger_id"), "R-076")
    add(rows, "manifest_successor", manifest.get("successor_gate") == "A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER", manifest.get("successor_gate"), "A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER")
    expected_negative = {
        "AUDIT-2026-07-25-A13-R075-COARSE-TRANSPORT-CRITICALITY",
        "NG-2026-07-25-A13-BREGMAN-AND-SEPARATED-SHIFTED-MULTIPLIER",
        "AUDIT-2026-07-25-A13-R076-PREDECESSOR-PASS-SCHEMAS",
        "AUDIT-2026-07-25-A13-R076-PRE-RELEASE-PROOF-AND-EVIDENCE-REPAIR",
    }
    add(rows, "manifest_negative_results", set(manifest.get("negative_results", [])) == expected_negative, manifest.get("negative_results"), sorted(expected_negative))

    for group_name in ("authority", "sources"):
        for key, record in manifest[group_name].items():
            path = REPO / record["path"]
            actual_hash = digest(path) if path.exists() else None
            add(rows, f"hash_{group_name}_{key}", actual_hash == record.get("sha256"), actual_hash, record.get("sha256"))

    predecessor_contracts: dict[str, dict[str, bool]] = {}
    for key in ("r050_manifest", "r063_manifest", "r066_manifest", "r071_manifest", "r073_manifest", "r075_manifest"):
        record = manifest["authority"][key]
        result_path = REPO / record["integrated_result_path"]
        result = json.loads(result_path.read_text(encoding="utf-8"))
        add(rows, f"predecessor_{key}_result_hash", digest(result_path) == record["integrated_result_sha256"], digest(result_path), record["integrated_result_sha256"])
        signals = {
            "summary": result.get("summary"),
            "assertion_summary": result.get("assertion_summary"),
            "verdict": result.get("verdict"),
            "status": result.get("status"),
            "pass": result["pass"] if "pass" in result else None,
        }
        add(rows, f"predecessor_{key}_pass", integrated_pass(result), signals, "internally consistent PASS")
        predecessor_contracts[key] = predecessor_contract(result, record)
    add(
        rows,
        "predecessor_internal_contracts",
        all(all(checks.values()) for checks in predecessor_contracts.values()),
        predecessor_contracts,
        "all schema-specific links and count fields coherent",
    )
    contradictory_records = [
        {"verdict": "PASS", "assertions": [{"status": "FAIL"}]},
        {"pass": True, "assertions": [{"status": "FAIL"}]},
        {"summary": {"failed": 0, "passed": 1, "total": 1}, "cross_assertions": [{"status": "FAIL"}]},
        {"status": "PASS", "assertions": []},
        {"verdict": "PASS", "assertions": [{"status": "PASS"}], "failures": ["hidden failure"]},
        {"pass": True, "assertions": [{"status": "PASS"}], "failure_stage": "child"},
    ]
    add(
        rows,
        "predecessor_parser_fail_closed",
        all(not integrated_pass(record) for record in contradictory_records),
        [integrated_pass(record) for record in contradictory_records],
        [False, False, False, False, False, False],
    )

    pdf_record = manifest["proof_pdf"]
    pdf_path = REPO / pdf_record["path"]
    pdf = pdf_contract(pdf_path)
    add(rows, "pdf_hash", digest(pdf_path) == pdf_record["sha256"], digest(pdf_path), pdf_record["sha256"])
    add(rows, "pdf_size", pdf_path.stat().st_size == pdf_record["size_bytes"], pdf_path.stat().st_size, pdf_record["size_bytes"])
    add(rows, "pdf_pages", pdf["pages"] == pdf_record["pages"], pdf["pages"], pdf_record["pages"])
    add(rows, "pdf_page_text", pdf["all_pages_have_text"], pdf["total_text_characters"], "every page has >100 extracted characters")
    add(rows, "pdf_form_check", pdf_record.get("form_check") == "PASS", pdf_record.get("form_check"), "PASS")
    add(rows, "pdf_overfull", pdf_record.get("overfull_hboxes") == 0, pdf_record.get("overfull_hboxes"), 0)
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS:"), pdf_record.get("visual_qa"), "PASS: ...")
    add(rows, "pdf_literal_control_debris", not pdf["literal_control_debris"], pdf["literal_control_debris"], [])

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note = note_path.read_text(encoding="utf-8")
    bare_qquads = [
        line_number
        for line_number, line in enumerate(note.splitlines(), start=1)
        if re.search(r"(?<!\\)qquad", line)
    ]
    add(rows, "note_literal_control_debris", not bare_qquads, bare_qquads, [])
    note_anchors = {
        "note_signed_ledger": "The nonduplicating signed endpoint ledger",
        "note_sharp_besov": "A sharpened cubic Besov theorem",
        "note_input_maximum": "largest \\emph{input} dyadic index",
        "note_closes": "What the correction closes",
        "note_shifted_boundary": r"fix $t\in(0,1]$",
        "note_bregman": "Affine Bregman and path positivity are false shortcuts",
        "note_causal_frontier": "The exact causal frontier",
        "note_evidence_map": "Evidence and failure map",
        "note_devil_review": "Devil's-advocate review",
        "note_p15": "R^{15}",
        "note_supercritical": "13/12>1",
        "note_result_footer": RESULT_ID,
        "note_no_overclaim": "No largest-root branch theorem",
    }
    for name, anchor in note_anchors.items():
        add(rows, name, anchor in note, anchor if anchor in note else "missing", anchor)

    repo_anchors = {
        "results_ledger_r076": (REPO / "RESULTS-LEDGER.md", ["R-076", "shifted-resonance"]),
        "roadmap_r076": (REPO / "ROADMAP.md", ["R-076", "coefficient-only balanced"]),
        "todo_r076": (REPO / "TODO.md", ["R-076", "coefficient-only balanced"]),
        "negative_audit": (REPO / "negative-results/registry.md", ["AUDIT-2026-07-25-A13-R075-COARSE-TRANSPORT-CRITICALITY", "1/15"]),
        "negative_shortcuts": (REPO / "negative-results/registry.md", ["NG-2026-07-25-A13-BREGMAN-AND-SEPARATED-SHIFTED-MULTIPLIER", "13/12"]),
        "claim_status": (CLAIM_DIR / "status.json", [RESULT_ID, "R-076"]),
        "changelog": (REPO / "CHANGELOG.md", ["R-076", "Besov"]),
    }
    for name, (path, anchors) in repo_anchors.items():
        content = path.read_text(encoding="utf-8")
        add(rows, name, all(anchor in content for anchor in anchors), [anchor for anchor in anchors if anchor in content], anchors)

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    add(rows, "primary_exit", primary_run["returncode"] == 0, primary_run, "returncode 0")
    add(rows, "independent_exit", independent_run["returncode"] == 0, independent_run, "returncode 0")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    add(rows, "primary_manifest_hash", primary.get("manifest_sha256") == manifest_hash, primary.get("manifest_sha256"), manifest_hash)
    add(rows, "independent_manifest_hash", independent.get("manifest_sha256") == manifest_hash, independent.get("manifest_sha256"), manifest_hash)
    primary_contract = child_contract(
        primary,
        PRIMARY,
        manifest_hash,
        "tect/a13-signed-transport-besov-bregman-resonance-primary/1.0",
        manifest["sources"]["primary"]["version"],
        EXPECTED_PRIMARY_ASSERTIONS,
    )
    independent_contract = child_contract(
        independent,
        INDEPENDENT,
        manifest_hash,
        "tect/a13-signed-transport-besov-bregman-resonance-independent/1.0",
        manifest["sources"]["independent"]["version"],
        EXPECTED_INDEPENDENT_ASSERTIONS,
    )
    add(rows, "primary_count", all(primary_contract.values()), primary_contract, "complete current-child contract")
    add(rows, "independent_count", all(independent_contract.values()), independent_contract, "complete current-child contract")

    add(rows, "cross_signed_ledger", primary["signed_ledger"]["max_direct_wick_error"] < 1.0e-10 and independent["ledger"]["max_direct_error"] < 1.0e-6, [primary["signed_ledger"], independent["ledger"]], "both below route tolerances")
    add(rows, "cross_payload_exponents", [primary["besov_budget"]["x_power"], primary["besov_budget"]["y_power"]] == [independent["exponents"]["x_power"], independent["exponents"]["y_power"]] == ["2/5", "8/15"], [primary["besov_budget"], independent["exponents"]], "2/5, 8/15")
    add(rows, "cross_young_slack", primary["besov_budget"]["young_slack"] == independent["exponents"]["slack"] == "1/15", [primary["besov_budget"]["young_slack"], independent["exponents"]["slack"]], "1/15")
    add(rows, "cross_moment", primary["besov_budget"]["required_moment"] == independent["exponents"]["moment"] == "15", [primary["besov_budget"]["required_moment"], independent["exponents"]["moment"]], "15")
    add(rows, "cross_young_losses", [primary["besov_budget"]["eta_loss_power"], primary["besov_budget"]["zeta_loss_power"]] == [independent["exponents"]["eta_power"], independent["exponents"]["zeta_power"]] == ["6", "8"], [primary["besov_budget"], independent["exponents"]], "eta^-6 zeta^-8")
    add(rows, "cross_bregman", abs(primary["bregman_fixture"]["remainder"] - independent["fixture"]["remainder"]) < 1.0e-9, [primary["bregman_fixture"]["remainder"], independent["fixture"]["remainder"]], "agreement <1e-9")
    add(rows, "cross_bregman_ratio", abs(primary["bregman_fixture"]["remainder_to_base"] + 3.0) < 1.0e-9 and abs(independent["fixture"]["ratio_to_base"] + 3.0) < 1.0e-7, [primary["bregman_fixture"]["remainder_to_base"], independent["fixture"]["ratio_to_base"]], -3.0)
    add(rows, "cross_selector_negative", primary["bregman_fixture"]["centered_selector_expectation"] < 0.0 and independent["fixture"]["selector_expectation"] < 0.0, [primary["bregman_fixture"]["centered_selector_expectation"], independent["fixture"]["selector_expectation"]], "both <0")
    add(rows, "cross_path_total", abs(primary["path_square_curvature"]["total_numeric"] + 1.5) < 1.0e-10 and abs(independent["path"]["total"] + 1.5) < 1.0e-6, [primary["path_square_curvature"]["total_numeric"], independent["path"]["total"]], -1.5)
    add(rows, "cross_radial_fourth", primary["shifted_multiplier"]["fourth_derivative_at_sqrt_floor"] == "-6/floor**(3/2)" and abs(independent["multiplier"]["fourth_derivative_normalized"] + 6.0) < 1.0e-12, [primary["shifted_multiplier"]["fourth_derivative_at_sqrt_floor"], independent["multiplier"]["fourth_derivative_normalized"]], "-6 e^(-3/2)")
    add(rows, "cross_multiplier_growth", max(abs(value - primary["shifted_multiplier"]["expected_doubling_ratio"]) for value in primary["shifted_multiplier"]["leakage_ratios"]) < 2.0e-6 and max(abs(value - independent["multiplier"]["expected_ratio"]) for value in independent["multiplier"]["ratios"]) < 3.0e-6, [primary["shifted_multiplier"]["leakage_ratios"], independent["multiplier"]["ratios"]], "dyadic ratio 2^s")
    add(rows, "cross_supercritical_sum", primary["shifted_multiplier"]["separated_budget_exponent_sum"] == independent["exponents"]["separated_sum"] == "13/12", [primary["shifted_multiplier"]["separated_budget_exponent_sum"], independent["exponents"]["separated_sum"]], "13/12")

    source_text = PRIMARY.read_text(encoding="utf-8")
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add(rows, "code_no_primary_import_in_independent", "signed_transport_besov_bregman_resonance import" not in independent_text and "import a13_classii_phase_kernel" not in independent_text, "no primary/runtime imports", "no primary/runtime imports")
    add(rows, "code_atomic_json", "tempfile.mkstemp" in source_text and "os.replace" in source_text and "tempfile.mkstemp" in independent_text and "os.replace" in independent_text, "atomic writer present", "atomic writer present")
    code_discipline = {
        "primary_moment_derived": "moment = 1 / slack" in source_text,
        "primary_report_not_literal": "s=3/5 payload: X^(2/5)" not in source_text,
        "independent_moment_derived": "\"moment\": str(1 / slack)" in independent_text,
        "independent_allocation_route": "interpolation_theta" in independent_text,
        "independent_avoids_primary_x_formula": "x_power = (1 + s) / 4" not in independent_text,
        "independent_avoids_primary_y_formula": "y_power = (7 - s) / 12" not in independent_text,
    }
    add(rows, "code_no_hardcoded_p15", all(code_discipline.values()), code_discipline, "derived report and independent interpolation allocation")
    add(rows, "scope_firewall_children", "remain open" in primary["honesty_boundary"] and "does not prove" in independent["honesty_boundary"], [primary["honesty_boundary"], independent["honesty_boundary"]], "explicit open boundaries")
    manifest_scope = {
        "honesty": all(token in manifest["honesty_boundary"] for token in ("remain open", "one-use", "Nelson", "T5--T7")),
        "multiplier_time": "fixed t>0" in manifest["theorem"]["separated_multiplier_boundary"],
    }
    add(rows, "scope_firewall_manifest", all(manifest_scope.values()), manifest_scope, "honesty boundary and nontrivial multiplier path time")

    passed = sum(row["status"] == "PASS" for row in rows)
    aggregate = EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + len(rows)
    expected_contract = manifest["verification"]
    add(rows, "manifest_primary_count", expected_contract["primary_assertions"] == EXPECTED_PRIMARY_ASSERTIONS, expected_contract["primary_assertions"], EXPECTED_PRIMARY_ASSERTIONS)
    add(rows, "manifest_independent_count", expected_contract["independent_assertions"] == EXPECTED_INDEPENDENT_ASSERTIONS, expected_contract["independent_assertions"], EXPECTED_INDEPENDENT_ASSERTIONS)
    # The final two count assertions are included in the integrated count.
    integrated_total = len(rows) + 2
    aggregate_total = EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + integrated_total
    add(rows, "manifest_integrated_count", expected_contract["integrated_assertions"] == integrated_total, expected_contract["integrated_assertions"], integrated_total)
    add(rows, "manifest_aggregate_count", expected_contract["aggregate_assertions"] == aggregate_total, expected_contract["aggregate_assertions"], aggregate_total)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-signed-transport-besov-bregman-resonance-integrated/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_version": __version__,
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": manifest_hash,
        "child_runs": {"primary": primary_run, "independent": independent_run},
        "child_outputs": {
            "primary": str(PRIMARY_OUTPUT.relative_to(REPO)).replace("\\", "/"),
            "independent": str(INDEPENDENT_OUTPUT.relative_to(REPO)).replace("\\", "/"),
        },
        "pdf_contract": pdf,
        "assertions": rows,
        "summary": {
            "passed": passed,
            "total": len(rows),
            "aggregate_assertions": EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + len(rows),
            "verdict": "PASS" if passed == len(rows) else "FAIL",
        },
        "honesty_boundary": manifest["honesty_boundary"],
        "source_sha256": digest(Path(__file__)),
    }
    atomic_json(output_path, payload)
    aggregate_final = payload["summary"]["aggregate_assertions"]
    if passed == len(rows):
        print(f"[R-076 integrated] {passed}/{len(rows)} PASS; aggregate {aggregate_final}/{aggregate_final} PASS")
    else:
        print(f"[R-076 integrated] {passed}/{len(rows)} FAIL; aggregate {passed + EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS}/{aggregate_final}")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: actual={row['actual']!r} expected={row['expected']!r}")
    print(f"result: {output_path.relative_to(REPO)}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(run())
