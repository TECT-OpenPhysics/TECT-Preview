#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A13 R-073 package."""

from __future__ import annotations

__version__ = "1.0.1"
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
DEFAULT_MANIFEST = CLAIM_DIR / "classii_off_diagonal_telescope_critical_phase_root_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-off-diagonal-telescope-critical-phase-root-reduction/result.json"
EXPECTED_RESULT = "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-REDUCTION"


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
            "schema": "tect/a13-off-diagonal-telescope-critical-phase-root-integrated/1.0",
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
        print("A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-INTEGRATED-PASS")
        print(f"Evidence: {output_path}")
        return 0

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-off-diagonal-telescope-critical-phase-root-reduction/1.0", manifest.get("schema"), "tect/a13-off-diagonal-telescope-critical-phase-root-reduction/1.0")
    add(rows, "manifest_result", manifest.get("result_id") == EXPECTED_RESULT, manifest.get("result_id"), EXPECTED_RESULT)
    add(rows, "manifest_ledger", manifest.get("result_ledger_id") == "R-073", manifest.get("result_ledger_id"), "R-073")
    for group in ("authority", "sources"):
        for key, record in manifest[group].items():
            path = REPO / record["path"]
            actual = digest(path)
            add(rows, f"hash_{group}_{key}", actual == record["sha256"], actual, record["sha256"])

    pdf_record = manifest["proof_pdf"]
    pdf_path = REPO / pdf_record["path"]
    add(rows, "hash_proof_pdf", digest(pdf_path) == pdf_record["sha256"], digest(pdf_path), pdf_record["sha256"])
    reader = PdfReader(str(pdf_path))
    add(rows, "pdf_pages", len(reader.pages) == int(pdf_record["pages"]), len(reader.pages), pdf_record["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == int(pdf_record["size_bytes"]), pdf_path.stat().st_size, pdf_record["size_bytes"])
    add(rows, "pdf_form_overfull", pdf_record.get("form_check") == "PASS" and int(pdf_record.get("overfull_hboxes", -1)) == 0, {"form": pdf_record.get("form_check"), "overfull": pdf_record.get("overfull_hboxes")}, {"form": "PASS", "overfull": 0})
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS"), pdf_record.get("visual_qa"), "PASS prefix")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = has_tokens(note_path, ["Familywise off-diagonal reassembly", "projector-free terminal completion", "theta>1/4", "theta<1/4", "theta>1/2", "theta<1/2", "p>{3\\over\\rho}", "finite-low boundary", "not a new lower bound"])
    add(rows, "note_scope_tokens", note_ok, note_missing, [])
    primary_path = REPO / manifest["sources"]["primary"]["path"]
    independent_path = REPO / manifest["sources"]["independent"]["path"]
    primary_ok, primary_missing = has_tokens(primary_path, ["full_reassembly", "projector_free_completion", "restored_phase_cancellation", "o2_thresholds_conflict", "o3_thresholds_conflict"])
    add(rows, "primary_scope_tokens", primary_ok, primary_missing, [])
    independent_ok, independent_missing = has_tokens(independent_path, ["independent_all_offdiagonal_nonzero", "projector_ranks_encoded", "restored_cancellation", "independent_gain_moment"])
    add(rows, "independent_scope_tokens", independent_ok, independent_missing, [])
    forbidden = [name for name in imported_modules(independent_path) if "off_diagonal_telescope_critical_phase_root" in name or "phase_kernel_causal_diagonal_reduction" in name]
    add(rows, "independent_non_importing", not forbidden, forbidden, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("hash_pdf_and_scope_preflight", False)

    prior_runs: dict[str, str] = {}
    for key in ("r069_manifest", "r070_manifest", "r071_manifest", "r072_manifest"):
        prior_manifest_path = REPO / manifest["authority"][key]["path"]
        prior_manifest = json.loads(prior_manifest_path.read_text(encoding="utf-8"))
        prior_contract_spec = prior_manifest.get("verification") or prior_manifest.get("run_contract")
        if not isinstance(prior_contract_spec, dict):
            add(rows, f"prior_{key}_contract_schema", False, list(prior_manifest), "verification or run_contract")
            continue
        prior_result_path = REPO / prior_contract_spec["integrated_output"]
        prior_result = json.loads(prior_result_path.read_text(encoding="utf-8"))
        prior_runs[key] = str(prior_result_path.relative_to(REPO)).replace("\\", "/")
        prior_pass = prior_result.get("pass") is True and prior_result.get("result_id") == prior_manifest.get("result_id") and prior_result.get("manifest_sha256") == digest(prior_manifest_path)
        add(rows, f"prior_{key}_result", prior_pass, {"pass": prior_result.get("pass"), "result": prior_result.get("result_id"), "manifest": prior_result.get("manifest_sha256")}, {"pass": True, "result": prior_manifest.get("result_id"), "manifest": digest(prior_manifest_path)})
        prior_rows = prior_result.get("assertions", [])
        prior_aggregate = prior_result.get("aggregate_assertion_count", prior_result.get("aggregate_assertions"))
        prior_contract = prior_result.get("assertion_count") == prior_contract_spec["integrated_assertions"] and prior_aggregate == prior_contract_spec["aggregate_assertions"] and len(prior_rows) == prior_contract_spec["integrated_assertions"] and all(row.get("status") == "PASS" for row in prior_rows)
        add(rows, f"prior_{key}_contract", prior_contract, {"integrated": prior_result.get("assertion_count"), "aggregate": prior_aggregate}, {"integrated": prior_contract_spec["integrated_assertions"], "aggregate": prior_contract_spec["aggregate_assertions"]})
    if not all(row["status"] == "PASS" for row in rows):
        return finish("prior_result_contracts", False, prior_runs)

    repository_checks = (
        ("results_ledger_r073", REPO / "RESULTS-LEDGER.md", ["R-073", "Exact off-diagonal telescope reassembly"]),
        ("status_result", CLAIM_DIR / "status.json", [EXPECTED_RESULT]),
        ("negative_result", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-RAW-ABSOLUTE-OFFDIAGONAL-CARLESON"]),
        ("evidence_map", REPO / "theory/proof-evidence-map.md", ["R-073", EXPECTED_RESULT]),
        ("sector_map", REPO / "governance/sector-a-theorem-map.json", ["R-073"]),
        ("exploration_log", REPO / "explorations/log.jsonl", ["EXP-000029", "EXP-000030", "EXP-000031"]),
        ("roadmap_successor", REPO / "ROADMAP.md", ["A13-CLASSII-ADAPTED-TERMINAL-PHASE-ROOT-COERCIVITY"]),
    )
    for name, path, tokens in repository_checks:
        ok, missing = has_tokens(path, tokens)
        add(rows, name, ok, missing, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("repository_integration_preflight", False, prior_runs)

    primary_process = execute(primary_path)
    independent_process = execute(independent_path)
    add(rows, "primary_exit", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "primary_sentinel", "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-PRIMARY-PASS" in primary_process.stdout, primary_process.stdout[-500:], "primary PASS sentinel")
    add(rows, "independent_exit", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "independent_sentinel", "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-INDEPENDENT-PASS" in independent_process.stdout, independent_process.stdout[-500:], "independent PASS sentinel")
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

    p = primary_result["derived"]
    i = independent_result["derived"]
    add(rows, "cross_full_reassembly", max(float(p["reassembly"]["max_residuals"]["full_reassembly"]), float(i["shell"]["max_residuals"]["full"])) < 1.0e-9, [p["reassembly"]["max_residuals"]["full_reassembly"], i["shell"]["max_residuals"]["full"]], "both <1e-9")
    add(rows, "cross_phase_slope", abs(float(p["phase"]["nonlinear_slope"]) - float(i["phase"]["nonlinear_slope"])) < 1.0e-12, [p["phase"]["nonlinear_slope"], i["phase"]["nonlinear_slope"]], "absolute difference <1e-12")
    add(rows, "cross_phase_cancellation", max(float(p["phase"]["restored_phase_cancellation"]), float(i["phase"]["restored_cancellation"])) < 1.0e-10, [p["phase"]["restored_phase_cancellation"], i["phase"]["restored_cancellation"]], "both <1e-10")
    add(rows, "cross_gain_moment", abs(float(p["critical_route"]["required_moment"]) - float(i["critical_route"]["moment"])) < 1.0e-12, [p["critical_route"]["required_moment"], i["critical_route"]["moment"]], "absolute difference <1e-12")

    add(rows, "integrated_count_contract", len(rows) + 2 == integrated_expected, len(rows) + 2, integrated_expected)
    aggregate_actual = primary_expected + independent_expected + len(rows) + 1
    add(rows, "aggregate_count_contract", aggregate_actual == aggregate_expected, aggregate_actual, aggregate_expected)
    passed = all(row["status"] == "PASS" for row in rows)
    child_runs = {**prior_runs, "primary": str(primary_result_path.relative_to(REPO)).replace("\\", "/"), "independent": str(independent_result_path.relative_to(REPO)).replace("\\", "/")}
    return finish("complete", passed, child_runs)


if __name__ == "__main__":
    raise SystemExit(run())
