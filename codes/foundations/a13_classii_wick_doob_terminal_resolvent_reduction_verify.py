#!/usr/bin/env python3
"""Integrated verifier for the A13 Wick--Doob/resolvent package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import argparse
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
DEFAULT_MANIFEST = CLAIM_DIR / "classii_wick_doob_terminal_resolvent_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-wick-doob-terminal-resolvent-reduction/result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
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


def text_tokens(path: Path, tokens: list[str]) -> tuple[bool, list[str]]:
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in tokens if token not in content]
    return not missing, missing


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = manifest["verification"]
    primary_expected = int(contract["primary_assertions"])
    independent_expected = int(contract["independent_assertions"])
    integrated_expected = int(contract["integrated_assertions"])
    aggregate_expected = int(contract["aggregate_assertions"])
    prior_integrated_expected = int(contract["prior_integrated_assertions"])
    rows: list[dict[str, Any]] = []

    def stop_before_stale_read(
        stage: str, child_runs: dict[str, str] | None = None
    ) -> int:
        payload = {
            "schema": "tect/a13-wick-doob-terminal-resolvent-integrated/1.0",
            "result_id": manifest["result_id"],
            "claim": manifest["claim"],
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
            "count_contract": {
                "integrated_expected": integrated_expected,
                "integrated_actual": len(rows),
                "aggregate_expected": aggregate_expected,
                "aggregate_actual": None,
            },
            "pass": False,
            "honesty_boundary": manifest["honesty_boundary"],
        }
        atomic_json(output_path, payload)
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        print(f"FAIL-CLOSED before stale evidence read: {stage}")
        return 1

    add(rows, "manifest_schema", manifest.get("schema") == "tect/a13-wick-doob-terminal-resolvent-reduction/1.0", manifest.get("schema"), "tect/a13-wick-doob-terminal-resolvent-reduction/1.0")
    add(rows, "manifest_result", manifest.get("result_id") == "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION", manifest.get("result_id"), "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION")
    add(rows, "manifest_ledger_id", manifest.get("result_ledger_id") == "R-070", manifest.get("result_ledger_id"), "R-070")
    for group in ("authority", "sources"):
        for key, record in manifest[group].items():
            actual = digest(REPO / record["path"])
            add(rows, f"hash_{group}_{key}", actual == record["sha256"], actual, record["sha256"])
    pdf_record = manifest["proof_pdf"]
    pdf_path = REPO / pdf_record["path"]
    add(rows, "hash_proof_pdf", digest(pdf_path) == pdf_record["sha256"], digest(pdf_path), pdf_record["sha256"])

    reader = PdfReader(str(pdf_path))
    add(rows, "pdf_pages", len(reader.pages) == pdf_record.get("pages"), len(reader.pages), pdf_record.get("pages"))
    add(
        rows,
        "pdf_form_and_overfull",
        pdf_record.get("form_check") == "PASS"
        and pdf_record.get("overfull_hboxes") == 0,
        {
            "form_check": pdf_record.get("form_check"),
            "overfull_hboxes": pdf_record.get("overfull_hboxes"),
        },
        {"form_check": "PASS", "overfull_hboxes": 0},
    )
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS"), pdf_record.get("visual_qa"), "PASS prefix")
    if not all(row["status"] == "PASS" for row in rows):
        return stop_before_stale_read("hash_and_pdf_preflight")

    primary_path = REPO / manifest["sources"]["primary"]["path"]
    independent_path = REPO / manifest["sources"]["independent"]["path"]
    primary_run = execute(primary_path)
    independent_run = execute(independent_path)
    add(rows, "primary_exit_zero", primary_run.returncode == 0, primary_run.returncode, 0)
    add(rows, "independent_exit_zero", independent_run.returncode == 0, independent_run.returncode, 0)
    if primary_run.returncode != 0 or independent_run.returncode != 0:
        return stop_before_stale_read(
            "child_execution",
            {
                "primary_stdout": primary_run.stdout,
                "primary_stderr": primary_run.stderr,
                "independent_stdout": independent_run.stdout,
                "independent_stderr": independent_run.stderr,
            },
        )
    primary_output = REPO / manifest["verification"]["primary_output"]
    independent_output = REPO / manifest["verification"]["independent_output"]
    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(rows, "primary_assertions", primary.get("assertion_count") == primary_expected, primary.get("assertion_count"), primary_expected)
    add(rows, "primary_result_id", primary.get("result_id") == manifest["result_id"], primary.get("result_id"), manifest["result_id"])
    add(rows, "primary_boundary", "remain open" in primary.get("honesty_boundary", ""), primary.get("honesty_boundary"), "contains remain open")
    add(rows, "independent_pass", independent.get("pass") is True, independent.get("pass"), True)
    add(rows, "independent_assertions", independent.get("assertion_count") == independent_expected, independent.get("assertion_count"), independent_expected)
    add(rows, "independent_result_id", independent.get("result_id") == manifest["result_id"], independent.get("result_id"), manifest["result_id"])
    add(rows, "independent_boundary", "does not prove" in independent.get("honesty_boundary", ""), independent.get("honesty_boundary"), "contains does not prove")
    independent_imports = imported_modules(independent_path)
    forbidden_imports = [item for item in independent_imports if "wick_doob_terminal_resolvent_reduction" in item or "endpoint_lifted" in item]
    add(rows, "independent_non_importing", not forbidden_imports, forbidden_imports, [])

    prior_manifest_record = manifest["authority"]["r069_manifest"]
    prior_manifest_path = REPO / prior_manifest_record["path"]
    prior_manifest = json.loads(
        prior_manifest_path.read_text(encoding="utf-8")
    )
    prior_output = REPO / prior_manifest["run_contract"]["integrated_output"]
    prior = json.loads(prior_output.read_text(encoding="utf-8"))
    prior_helper = prior_manifest["sources"]["primary"]
    prior_helper_actual = digest(REPO / prior_helper["path"])
    prior_manifest_actual = digest(prior_manifest_path)
    add(
        rows,
        "r069_prior_pass_and_imported_helper_pin",
        prior.get("pass") is True
        and prior.get("manifest_sha256") == prior_manifest_actual
        and prior_helper_actual == prior_helper["sha256"],
        {
            "prior_pass": prior.get("pass"),
            "prior_manifest_sha256": prior.get("manifest_sha256"),
            "helper_sha256": prior_helper_actual,
        },
        {
            "prior_pass": True,
            "prior_manifest_sha256": prior_manifest_actual,
            "helper_sha256": prior_helper["sha256"],
        },
    )
    add(rows, "r069_prior_assertions", prior.get("assertion_count") == prior_integrated_expected, prior.get("assertion_count"), prior_integrated_expected)

    token_checks: list[tuple[str, str, list[str]]] = [
        (
            "note",
            manifest["sources"]["proof_note"]["path"],
            [
                "Exact Wick--Doob transport",
                "Raw terminal-minus-injection form and trace restoration",
                "Exact retained terminal resolvent",
                "Adapted centering and Stein no-go diagnostics",
                "The exact non-circular successor",
                "A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION (R-070)",
            ],
        ),
        (
            "status",
            "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/status.json",
            ["R-070", "Wick--Doob", "non-pp", "rational-frame/cross-square"],
        ),
        (
            "claim",
            "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/claim.md",
            ["R-070", "terminal covariance-normal current", "q11", "non-`pp`"],
        ),
        (
            "results",
            "RESULTS-LEDGER.md",
            ["R-070", "Wick--Doob terminalization and adapted-resolvent boundary", "adapted centered-resolvent chaos"],
        ),
        (
            "roadmap",
            "ROADMAP.md",
            ["R-070", "non-`pp`", "rational-frame/cross-square"],
        ),
        (
            "gates",
            "claims/GATES.md",
            ["R-070", "terminal translated-current", "non-`pp`", "cross-square"],
        ),
        (
            "todo",
            "TODO.md",
            ["R-070", "non-pp", "finite-energy extension"],
        ),
        (
            "sector_map",
            "governance/sector-a-theorem-map.json",
            ["R-070", "non-pp", "rational-frame/cross-square"],
        ),
        (
            "proof_map",
            "theory/proof-evidence-map.md",
            ["R-070", "Wick--Doob", "adapted centered-resolvent"],
        ),
        (
            "negative",
            "negative-results/registry.md",
            ["NG-2026-07-24-A13-DOOB-RESOLVENT-CLOSURE", "AUDIT-2026-07-24-A13-R070-LINEAR-FRAME-OMISSION", "Malliavin"],
        ),
        (
            "explorations",
            "explorations/log.jsonl",
            ["Wick--Doob terminalization", "terminal resolvent", "EXP-000018"],
        ),
        (
            "changelog",
            "CHANGELOG.md",
            ["Prove A13 Wick--Doob terminalization", "Repair R-070 weighted linear-frame decomposition", "R-070"],
        ),
        (
            "lineage",
            "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/LINEAGE.md",
            ["classii-wick-doob-terminal-resolvent-reduction", "v1.0", "R-070"],
        ),
        (
            "index",
            "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/INDEX.md",
            ["classii-wick-doob-terminal-resolvent-reduction", "T4", "balanced linear-frame model lemma"],
        ),
    ]
    for name, relative, tokens in token_checks:
        ok, missing = text_tokens(REPO / relative, tokens)
        add(rows, f"integration_{name}", ok, missing, [])

    theorem_keys = set(manifest.get("theorem", {}))
    required_theorem_keys = {
        "wick_doob",
        "full_current",
        "trace_restoration",
        "transported_tail",
        "endpoint_defect",
        "terminal_equivalence",
        "retained_resolvent",
        "adapted_no_go",
        "weighted_linear_split",
        "two_stage_successor",
    }
    add(rows, "manifest_theorem_complete", required_theorem_keys <= theorem_keys, sorted(theorem_keys), sorted(required_theorem_keys))
    add(rows, "manifest_honesty", "does not prove" in manifest.get("honesty_boundary", ""), manifest.get("honesty_boundary"), "contains does not prove")
    add(rows, "successor_is_two_stage", "two exact non-circular stages" in manifest.get("successor", ""), manifest.get("successor"), "contains two exact non-circular stages")

    aggregate_actual = (
        int(primary.get("assertion_count", -1))
        + int(independent.get("assertion_count", -1))
        + len(rows)
    )
    count_contract_ok = len(rows) == integrated_expected
    aggregate_contract_ok = aggregate_actual == aggregate_expected
    passed = (
        all(row["status"] == "PASS" for row in rows)
        and count_contract_ok
        and aggregate_contract_ok
    )
    payload = {
        "schema": "tect/a13-wick-doob-terminal-resolvent-integrated/1.0",
        "result_id": manifest["result_id"],
        "claim": manifest["claim"],
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "child_runs": {
            "primary_stdout": primary_run.stdout,
            "independent_stdout": independent_run.stdout,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "aggregate_assertion_count": aggregate_actual,
        "count_contract": {
            "integrated_expected": integrated_expected,
            "integrated_actual": len(rows),
            "aggregate_expected": aggregate_expected,
            "aggregate_actual": aggregate_actual,
        },
        "pass": passed,
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if not passed:
        if not count_contract_ok:
            print(f"FAIL integrated assertion contract: {len(rows)} expected {integrated_expected}")
        if not aggregate_contract_ok:
            print(f"FAIL aggregate assertion contract: {aggregate_actual} expected {aggregate_expected}")
        for row in rows:
            if row["status"] != "PASS":
                print(f"FAIL {row['name']}: {row['actual']} expected {row['expected']}")
        return 1
    print(f"PRIMARY: {primary_expected}/{primary_expected} PASS")
    print(f"INDEPENDENT: {independent_expected}/{independent_expected} PASS")
    print(f"ASSERTS: {len(rows)}/{len(rows)}")
    print(f"AGGREGATE: {payload['aggregate_assertion_count']}/{payload['aggregate_assertion_count']}")
    print("A13-CLASSII-WICK-DOOB-TERMINAL-RESOLVENT-REDUCTION-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    manifest = arguments.manifest if arguments.manifest.is_absolute() else REPO / arguments.manifest
    output = arguments.output if arguments.output.is_absolute() else REPO / arguments.output
    return run(manifest, output)


if __name__ == "__main__":
    raise SystemExit(main())
