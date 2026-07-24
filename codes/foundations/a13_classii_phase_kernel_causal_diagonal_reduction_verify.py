#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A13 R-072 package."""

from __future__ import annotations

__version__ = "1.0.0"
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
DEFAULT_MANIFEST = CLAIM_DIR / "classii_phase_kernel_causal_diagonal_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-phase-kernel-causal-diagonal-reduction/result.json"


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
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def execute(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        errors="replace",
    )


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

    def finish_failure(stage: str, child_runs: dict[str, str] | None = None) -> int:
        payload = {
            "schema": "tect/a13-phase-kernel-causal-diagonal-integrated/1.0",
            "result_id": manifest.get("result_id"),
            "claim": manifest.get("claim"),
            "date": "2026-07-24",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "script_version": __version__,
            "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": digest(manifest_path),
            "failure_stage": stage,
            "child_runs": child_runs or {},
            "assertions": rows,
            "assertion_count": len(rows),
            "aggregate_assertion_count": None,
            "pass": False,
            "honesty_boundary": manifest.get("honesty_boundary"),
        }
        atomic_json(output_path, payload)
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        print(f"FAIL-CLOSED at {stage}")
        return 1

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-phase-kernel-causal-diagonal-reduction/1.0", manifest.get("schema"), "tect/a13-phase-kernel-causal-diagonal-reduction/1.0")
    add(rows, "manifest_result", manifest.get("result_id") == "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-ONE-USE-REDUCTION", manifest.get("result_id"), "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-ONE-USE-REDUCTION")
    add(rows, "manifest_ledger", manifest.get("result_ledger_id") == "R-072", manifest.get("result_ledger_id"), "R-072")
    for group in ("authority", "sources"):
        for key, record in manifest[group].items():
            path = REPO / record["path"]
            actual = digest(path)
            add(rows, f"hash_{group}_{key}", actual == record["sha256"], actual, record["sha256"])

    pdf_record = manifest["proof_pdf"]
    pdf_path = REPO / pdf_record["path"]
    actual_pdf_hash = digest(pdf_path)
    add(rows, "hash_proof_pdf", actual_pdf_hash == pdf_record["sha256"], actual_pdf_hash, pdf_record["sha256"])
    reader = PdfReader(str(pdf_path))
    add(rows, "pdf_pages", len(reader.pages) == int(pdf_record["pages"]), len(reader.pages), pdf_record["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == int(pdf_record["size_bytes"]), pdf_path.stat().st_size, pdf_record["size_bytes"])
    add(rows, "pdf_form_overfull", pdf_record.get("form_check") == "PASS" and int(pdf_record.get("overfull_hboxes", -1)) == 0, {"form": pdf_record.get("form_check"), "overfull": pdf_record.get("overfull_hboxes")}, {"form": "PASS", "overfull": 0})
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS"), pdf_record.get("visual_qa"), "PASS prefix")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = has_tokens(
        note_path,
        [
            "exact gauge kernel",
            "432\\eta^3",
            "5\\over126",
            "expectation-only",
            "Exact off-diagonal remainder",
            "4087",
            "gamma-\\delta",
            "finite-low boundary",
        ],
    )
    add(rows, "note_scope_tokens", note_ok, note_missing, [])
    primary_path = REPO / manifest["sources"]["primary"]["path"]
    independent_path = REPO / manifest["sources"]["independent"]["path"]
    primary_ok, primary_missing = has_tokens(primary_path, ["exact_gauge_kernel", "one_constant_tail_coefficient", "terminal_leakage_off_diagonal_identity", "off_diagonal_remainder_nonzero"])
    add(rows, "primary_scope_tokens", primary_ok, primary_missing, [])
    independent_ok, independent_missing = has_tokens(independent_path, ["independent_exact_gauge_kernel", "independent_tail_factor", "independent_off_diagonal_load_bearing", "off_to_diagonal_ratio"])
    add(rows, "independent_scope_tokens", independent_ok, independent_missing, [])
    forbidden = [name for name in imported_modules(independent_path) if "phase_kernel_causal_diagonal_reduction" in name]
    add(rows, "independent_non_importing", not forbidden, forbidden, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish_failure("hash_pdf_and_scope_preflight")

    prior_manifest_path = REPO / manifest["authority"]["r071_manifest"]["path"]
    prior_manifest = json.loads(prior_manifest_path.read_text(encoding="utf-8"))
    prior_result_path = REPO / prior_manifest["verification"]["integrated_output"]
    prior_result = json.loads(prior_result_path.read_text(encoding="utf-8"))
    prior_pass = (
        prior_result.get("pass") is True
        and prior_result.get("result_id") == prior_manifest.get("result_id")
        and prior_result.get("manifest_sha256") == digest(prior_manifest_path)
    )
    add(rows, "prior_r071_result_pass", prior_pass, {"pass": prior_result.get("pass"), "result_id": prior_result.get("result_id"), "manifest_sha256": prior_result.get("manifest_sha256")}, {"pass": True, "result_id": prior_manifest.get("result_id"), "manifest_sha256": digest(prior_manifest_path)})
    prior_rows = prior_result.get("assertions", [])
    prior_count = (
        prior_result.get("assertion_count") == prior_manifest["verification"]["integrated_assertions"]
        and prior_result.get("aggregate_assertion_count") == prior_manifest["verification"]["aggregate_assertions"]
        and len(prior_rows) == prior_manifest["verification"]["integrated_assertions"]
        and all(row.get("status") == "PASS" for row in prior_rows)
    )
    add(rows, "prior_r071_assertion_contract", prior_count, {"integrated": prior_result.get("assertion_count"), "aggregate": prior_result.get("aggregate_assertion_count"), "failed": [row.get("name") for row in prior_rows if row.get("status") != "PASS"]}, {"integrated": prior_manifest["verification"]["integrated_assertions"], "aggregate": prior_manifest["verification"]["aggregate_assertions"], "failed": []})
    if not all(row["status"] == "PASS" for row in rows):
        return finish_failure("prior_r071_result_contract")

    primary_process = execute(primary_path)
    independent_process = execute(independent_path)
    add(rows, "primary_exit", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "primary_sentinel", "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-PRIMARY-PASS" in primary_process.stdout, primary_process.stdout[-500:], "primary PASS sentinel")
    add(rows, "independent_exit", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "independent_sentinel", "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-INDEPENDENT-PASS" in independent_process.stdout, independent_process.stdout[-500:], "independent PASS sentinel")
    if not all(row["status"] == "PASS" for row in rows):
        return finish_failure("child_execution", {"primary": primary_process.stdout + primary_process.stderr, "independent": independent_process.stdout + independent_process.stderr})

    primary_result_path = REPO / contract["primary_output"]
    independent_result_path = REPO / contract["independent_output"]
    primary_result = json.loads(primary_result_path.read_text(encoding="utf-8"))
    independent_result = json.loads(independent_result_path.read_text(encoding="utf-8"))
    add(rows, "primary_result_pass", primary_result.get("pass") is True, primary_result.get("pass"), True)
    add(rows, "independent_result_pass", independent_result.get("pass") is True, independent_result.get("pass"), True)
    add(rows, "primary_count", int(primary_result.get("assertion_count", -1)) == primary_expected, primary_result.get("assertion_count"), primary_expected)
    add(rows, "independent_count", int(independent_result.get("assertion_count", -1)) == independent_expected, independent_result.get("assertion_count"), independent_expected)

    p = primary_result["derived"]
    i = independent_result["derived"]
    p_cstar = float(p["local_bound"]["c_star"])
    i_cstar = float(i["local"]["c_star"])
    add(rows, "independent_cstar_agreement", abs(p_cstar - i_cstar) < 1.0e-13, {"primary": p_cstar, "independent": i_cstar}, "absolute difference <1e-13")
    p_slope = float(p["fixture"]["leakage_slope"])
    i_slope = float(i["fixture"]["slope"])
    add(rows, "independent_gauge_slope_agreement", abs(p_slope - i_slope) < 5.0e-8, {"primary": p_slope, "independent": i_slope}, "absolute difference <5e-8")
    add(rows, "independent_off_diagonal_ratio", float(i["off_diagonal"]["off_to_diagonal_ratio"]) > 4000.0, i["off_diagonal"]["off_to_diagonal_ratio"], ">4000")
    p_tail = float(p["sequence_tail"]["tail_after_young"])
    i_tail = float(i["scalar_budget"]["tail_factor"])
    add(rows, "independent_tail_agreement", abs(p_tail - i_tail) < 1.0e-15, {"primary": p_tail, "independent": i_tail}, "absolute difference <1e-15")

    add(rows, "integrated_count_contract", len(rows) + 2 == integrated_expected, len(rows) + 2, integrated_expected)
    aggregate_actual = primary_expected + independent_expected + len(rows) + 1
    add(rows, "aggregate_count_contract", aggregate_actual == aggregate_expected, aggregate_actual, aggregate_expected)
    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-phase-kernel-causal-diagonal-integrated/1.0",
        "result_id": manifest["result_id"],
        "claim": manifest["claim"],
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "child_runs": {
            "prior_r071": str(prior_result_path.relative_to(REPO)).replace("\\", "/"),
            "primary": str(primary_result_path.relative_to(REPO)).replace("\\", "/"),
            "independent": str(independent_result_path.relative_to(REPO)).replace("\\", "/"),
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "aggregate_assertion_count": primary_expected + independent_expected + len(rows),
        "count_contract": {"primary": primary_expected, "independent": independent_expected, "integrated": integrated_expected, "aggregate": aggregate_expected},
        "pass": passed,
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    print(f"{sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print(f"AGGREGATE {primary_expected + independent_expected + len(rows)}/{aggregate_expected} PASS" if passed else "AGGREGATE FAIL")
    print("A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-INTEGRATED-PASS" if passed else "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-INTEGRATED-FAIL")
    print(f"Evidence: {output_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())
