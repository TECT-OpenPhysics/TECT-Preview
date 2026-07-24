#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A13 R-074 package."""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM_DIR / "classii_resonant_phase_root_besov_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-resonant-phase-root-besov-reduction/result.json"
EXPECTED_RESULT = "A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-REDUCTION"


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


def execute(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(path)], cwd=REPO, capture_output=True, text=True, errors="replace")


def imported_modules(path: Path) -> list[str]:
    modules: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def has_tokens(path: Path, tokens: list[str]) -> tuple[bool, list[str]]:
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in tokens if token not in content]
    return not missing, missing


def prior_integrated_pass(manifest_path: Path) -> tuple[bool, dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = manifest.get("verification") or manifest.get("run_contract")

    if isinstance(contract, dict) and "integrated_output" in contract:
        result_path = REPO / contract["integrated_output"]
        result = json.loads(result_path.read_text(encoding="utf-8"))
        rows = result.get("assertions", result.get("cross_assertions", []))
        integrated_expected = int(
            contract.get("integrated_assertions", contract.get("integrated_own_assertions", -1))
        )
        aggregate_expected = int(
            contract.get("aggregate_assertions", contract.get("expected_total_assertions", -1))
        )
        summary = result.get("summary", {})
        pass_signal = result.get("pass") is True or (
            isinstance(summary, dict)
            and int(summary.get("failed", -1)) == 0
            and str(result.get("verdict", "")).endswith("INTEGRATED-PASS")
        )
        assertion_count = result.get("assertion_count", len(rows))
        aggregate_count = result.get(
            "aggregate_assertion_count",
            result.get("aggregate_assertions", summary.get("total")),
        )
        passed = (
            pass_signal
            and result.get("result_id") == manifest.get("result_id")
            and result.get("manifest_sha256") == digest(manifest_path)
            and int(assertion_count) == integrated_expected
            and int(aggregate_count) == aggregate_expected
            and len(rows) == integrated_expected
            and all(row.get("status") == "PASS" for row in rows)
        )
        return passed, {
            "schema": "verification" if "verification" in manifest else "run_contract",
            "result": str(result_path.relative_to(REPO)).replace("\\", "/"),
            "pass_signal": pass_signal,
            "result_id": result.get("result_id"),
            "manifest_sha256": result.get("manifest_sha256"),
            "assertion_count": assertion_count,
            "aggregate": aggregate_count,
        }

    if manifest.get("schema") == "tect/a6-classii-k-composite/1.0":
        result_path = manifest_path.parent / "runs/2026-07-20-integrated-k-composite/result.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        rows = result.get("assertions", [])
        summary = result.get("assertion_summary", {})
        source_reports = result.get("source_reports", {})
        passed = (
            result.get("verdict") == "A6-CLASSII-K-COMPOSITE-INTEGRATED-PASS"
            and result.get("failures") == []
            and source_reports.get("manifest_sha256") == digest(manifest_path)
            and int(summary.get("integrated_total", -1)) == 19
            and int(summary.get("integrated_passed", -1)) == 19
            and int(summary.get("primary_total", -1)) == 29
            and int(summary.get("independent_total", -1)) == 16
            and int(summary.get("aggregate_total", -1)) == 64
            and len(rows) == 19
            and all(row.get("status") == "PASS" for row in rows)
        )
        return passed, {
            "schema": "legacy-a6-k-composite",
            "result": str(result_path.relative_to(REPO)).replace("\\", "/"),
            "verdict": result.get("verdict"),
            "manifest_sha256": source_reports.get("manifest_sha256"),
            "counts": summary,
        }

    return False, {"error": "unrecognized predecessor integrated contract schema"}


def run(manifest_path: Path = DEFAULT_MANIFEST, output_path: Path = DEFAULT_OUTPUT) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = manifest["verification"]
    primary_expected = int(contract["primary_assertions"])
    independent_expected = int(contract["independent_assertions"])
    integrated_expected = int(contract["integrated_assertions"])
    aggregate_expected = int(contract["aggregate_assertions"])
    rows: list[dict[str, Any]] = []

    def finish(stage: str, passed: bool, child_runs: dict[str, str] | None = None) -> int:
        payload = {
            "schema": "tect/a13-resonant-phase-root-besov-integrated/1.0",
            "result_id": manifest.get("result_id"),
            "claim": manifest.get("claim"),
            "date": "2026-07-24",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "script_version": __version__,
            "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": digest(manifest_path),
            "failure_stage": None if passed else stage,
            "child_runs": child_runs or {},
            "assertions": rows,
            "assertion_count": len(rows),
            "aggregate_assertion_count": primary_expected + independent_expected + len(rows) if passed else None,
            "count_contract": {"primary": primary_expected, "independent": independent_expected, "integrated": integrated_expected, "aggregate": aggregate_expected},
            "pass": passed,
            "honesty_boundary": manifest.get("honesty_boundary"),
        }
        atomic_json(output_path, payload)
        if not passed:
            for row in rows:
                if row["status"] != "PASS":
                    print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
            print(f"FAIL-CLOSED at {stage}")
            return 1
        print(f"Integrated assertions: {len(rows)}/{integrated_expected} PASS")
        print(f"AGGREGATE {primary_expected + independent_expected + len(rows)}/{aggregate_expected} PASS")
        print("A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-INTEGRATED-PASS")
        print(f"Evidence: {output_path}")
        return 0

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-resonant-phase-root-besov-reduction/1.0", manifest.get("schema"), "tect/a13-resonant-phase-root-besov-reduction/1.0")
    add(rows, "manifest_result", manifest.get("result_id") == EXPECTED_RESULT, manifest.get("result_id"), EXPECTED_RESULT)
    add(rows, "manifest_ledger", manifest.get("result_ledger_id") == "R-074", manifest.get("result_ledger_id"), "R-074")
    for group in ("authority", "sources"):
        for key, record in manifest[group].items():
            path = REPO / record["path"]
            actual = digest(path)
            add(rows, f"hash_{group}_{key}", actual == record["sha256"], actual, record["sha256"])
    required_runtime_authorities = {
        "r072_runtime_manifest",
        "r072_runtime_source",
        "uv_runtime_manifest",
        "uv_runtime_source",
    }
    add(
        rows,
        "runtime_dependencies_directly_pinned",
        required_runtime_authorities.issubset(manifest["authority"]),
        sorted(required_runtime_authorities.intersection(manifest["authority"])),
        sorted(required_runtime_authorities),
    )

    pdf_record = manifest["proof_pdf"]
    pdf_path = REPO / pdf_record["path"]
    add(rows, "hash_proof_pdf", digest(pdf_path) == pdf_record["sha256"], digest(pdf_path), pdf_record["sha256"])
    reader = PdfReader(str(pdf_path))
    add(rows, "pdf_pages", len(reader.pages) == int(pdf_record["pages"]), len(reader.pages), pdf_record["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == int(pdf_record["size_bytes"]), pdf_path.stat().st_size, pdf_record["size_bytes"])
    add(rows, "pdf_form_overfull", pdf_record.get("form_check") == "PASS" and int(pdf_record.get("overfull_hboxes", -1)) == 0, {"form": pdf_record.get("form_check"), "overfull": pdf_record.get("overfull_hboxes")}, {"form": "PASS", "overfull": 0})
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS"), pdf_record.get("visual_qa"), "PASS prefix")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = has_tokens(note_path, [
        "Frozen principal resonance", "Pure phase-orbit Wick theorem",
        "Besov one-use discriminator", "Cameron--Martin rescue boundary",
        "finite-energy recovery", "horizontal terminal coercivity open",
    ])
    add(rows, "note_scope_tokens", note_ok, note_missing, [])
    primary_path = REPO / manifest["sources"]["primary"]["path"]
    independent_path = REPO / manifest["sources"]["independent"]["path"]
    primary_ok, primary_missing = has_tokens(primary_path, ["frozen_principal", "phase_feedback", "phase_covariance_anomaly", "besov_budget", "cameron_martin_rescue"])
    add(rows, "primary_scope_tokens", primary_ok, primary_missing, [])
    independent_ok, independent_missing = has_tokens(independent_path, ["principal_and_secant", "phase_diagnostics", "covariance_tail", "independent_Besov_budget_slack"])
    add(rows, "independent_scope_tokens", independent_ok, independent_missing, [])
    forbidden = [name for name in imported_modules(independent_path) if "a13_classii_resonant_phase_root_besov" in name or "a13_classii_phase_kernel" in name or "a6_classii_uv" in name]
    add(rows, "independent_non_importing", not forbidden, forbidden, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("hash_pdf_and_scope_preflight", False)

    prior_runs: dict[str, str] = {}
    for key in ("r050_manifest", "r063_manifest", "r073_manifest"):
        prior_path = REPO / manifest["authority"][key]["path"]
        prior_pass, details = prior_integrated_pass(prior_path)
        prior_runs[key] = str(details.get("result", "missing"))
        add(rows, f"prior_{key}_integrated_contract", prior_pass, details, "hash-pinned integrated PASS")
    if not all(row["status"] == "PASS" for row in rows):
        return finish("prior_result_contracts", False, prior_runs)

    repository_checks = (
        ("results_ledger_r074", REPO / "RESULTS-LEDGER.md", ["R-074", "phase-root"]),
        ("status_result", CLAIM_DIR / "status.json", [EXPECTED_RESULT]),
        ("negative_bare_gain", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-RAW-BARE-POSITIVE-GAIN-ROOT"]),
        ("negative_centering", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-AUTOMATIC-ADAPTED-WICK-CENTERING"]),
        ("evidence_map", REPO / "theory/proof-evidence-map.md", ["R-074", EXPECTED_RESULT]),
        ("sector_map", REPO / "governance/sector-a-theorem-map.json", ["R-074"]),
        ("exploration_log", REPO / "explorations/log.jsonl", ["EXP-000032", "EXP-000033", "EXP-000034", "EXP-000035"]),
        ("roadmap_successor", REPO / "ROADMAP.md", ["A13-CLASSII-ADAPTED-GAUGE-QUOTIENT-TAYLOR-ONE-FORM"]),
    )
    for name, path, tokens in repository_checks:
        ok, missing = has_tokens(path, tokens)
        add(rows, name, ok, missing, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("repository_integration_preflight", False, prior_runs)

    primary_process = execute(primary_path)
    independent_process = execute(independent_path)
    add(rows, "primary_exit", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "primary_sentinel", "A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-PRIMARY-PASS" in primary_process.stdout, primary_process.stdout[-700:], "primary PASS sentinel")
    add(rows, "independent_exit", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "independent_sentinel", "A13-CLASSII-RESONANT-PHASE-ROOT-BESOV-INDEPENDENT-PASS" in independent_process.stdout, independent_process.stdout[-700:], "independent PASS sentinel")
    if not all(row["status"] == "PASS" for row in rows):
        return finish("child_execution", False, {**prior_runs, "primary": primary_process.stdout + primary_process.stderr, "independent": independent_process.stdout + independent_process.stderr})

    primary_result_path = REPO / contract["primary_output"]
    independent_result_path = REPO / contract["independent_output"]
    primary_result = json.loads(primary_result_path.read_text(encoding="utf-8"))
    independent_result = json.loads(independent_result_path.read_text(encoding="utf-8"))
    add(rows, "primary_result_pass", primary_result.get("pass") is True, primary_result.get("pass"), True)
    add(rows, "independent_result_pass", independent_result.get("pass") is True, independent_result.get("pass"), True)
    add(rows, "primary_count", primary_result.get("assertion_count") == primary_expected, primary_result.get("assertion_count"), primary_expected)
    add(rows, "independent_count", independent_result.get("assertion_count") == independent_expected, independent_result.get("assertion_count"), independent_expected)
    add(rows, "primary_source_hash_selfcheck", primary_result["source"]["sha256"] == digest(primary_path), primary_result["source"]["sha256"], digest(primary_path))
    add(rows, "independent_source_hash_selfcheck", independent_result["source"]["sha256"] == digest(independent_path), independent_result["source"]["sha256"], digest(independent_path))

    p = primary_result["derived"]
    i = independent_result["derived"]
    add(rows, "cross_principal_coefficient", abs(float(p["principal"]["analytic_contraction"]) - float(i["principal_and_secant"]["exact_principal"])) < 1.0e-13, [p["principal"]["analytic_contraction"], i["principal_and_secant"]["exact_principal"]], "absolute difference<1e-13")
    add(rows, "cross_phase_feedback_lambda", abs(float(p["phase_feedback"]["lambda_formula"]) - float(i["phase"]["lambda_expected"])) < 1.0e-13, [p["phase_feedback"]["lambda_formula"], i["phase"]["lambda_expected"]], "absolute difference<1e-13")
    add(rows, "cross_phase_feedback_mean", abs(float(p["phase_feedback"]["exact_wick_expectation"]) - float(i["phase"]["negative_feedback_mean"])) < 1.0e-13, [p["phase_feedback"]["exact_wick_expectation"], i["phase"]["negative_feedback_mean"]], "absolute difference<1e-13")
    p_cutoff_norm = float(p["phase_covariance_anomaly"]["rows"][-1]["perpendicular_norm"])
    i_cutoff_norm = float(i["covariance_tail"]["perpendicular_norms"][-1])
    add(rows, "cross_covariance_perpendicular_cutoff", abs(p_cutoff_norm - i_cutoff_norm) < 1.0e-13, [p_cutoff_norm, i_cutoff_norm], "absolute difference<1e-13")
    add(rows, "cross_covariance_tail_power", float(p["phase_covariance_anomaly"]["diagnostic_tail_slope"]) < -2.8 and float(i["covariance_tail"]["successive_slopes"][-1]) < -2.8, [p["phase_covariance_anomaly"]["diagnostic_tail_slope"], i["covariance_tail"]["successive_slopes"][-1]], "both<-2.8; analytic=-3")
    add(rows, "cross_local_phase_invariance", max(float(p["local_phase_covariance"]["current_invariance_error"]), float(i["phase"]["local_phase_current_error"])) < 1.0e-10, [p["local_phase_covariance"]["current_invariance_error"], i["phase"]["local_phase_current_error"]], "both<1e-10")
    add(rows, "cross_Besov_sixth_moment", abs(float(p["besov_budget"]["random_moment_power"]) - 6.0) < 1.0e-12, p["besov_budget"], "moment=6")
    add(rows, "cross_no_bare_gain", float(p["separation"]["separation_spread"]) < 1.0e-12 and float(i["principal_and_secant"]["secant_spread"]) < 1.0e-12, [p["separation"]["separation_spread"], i["principal_and_secant"]["secant_spread"]], "both zero")
    add(rows, "scope_firewall_keeps_horizontal_gate_open", "remain open" in primary_result["honesty_boundary"] and "remain open" in independent_result["honesty_boundary"], [primary_result["honesty_boundary"], independent_result["honesty_boundary"]], "explicit open boundary")

    add(rows, "integrated_count_contract", len(rows) + 2 == integrated_expected, len(rows) + 2, integrated_expected)
    aggregate_actual = primary_expected + independent_expected + len(rows) + 1
    add(rows, "aggregate_count_contract", aggregate_actual == aggregate_expected, aggregate_actual, aggregate_expected)
    passed = all(row["status"] == "PASS" for row in rows)
    child_runs = {**prior_runs, "primary": str(primary_result_path.relative_to(REPO)).replace("\\", "/"), "independent": str(independent_result_path.relative_to(REPO)).replace("\\", "/")}
    return finish("complete", passed, child_runs)


if __name__ == "__main__":
    raise SystemExit(run())
