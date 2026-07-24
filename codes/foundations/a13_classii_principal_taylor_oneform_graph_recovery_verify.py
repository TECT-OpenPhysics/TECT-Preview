#!/usr/bin/env python3
"""Fail-closed integrated verifier for the A13 R-075 package."""

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
DEFAULT_MANIFEST = CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json"
EXPECTED_RESULT = "A13-CLASSII-PRINCIPAL-TAYLOR-ONE-FORM-GRAPH-RECOVERY-REDUCTION"
EXPECTED_CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
EXPECTED_SUCCESSOR = "A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER"
EXPECTED_NEGATIVES = [
    "NG-2026-07-24-A13-ABSOLUTE-THIRD-ORDER-TRANSPORT",
    "NG-2026-07-24-A13-ONEFORM-ONLY-ENDPOINT-OMISSION",
    "NG-2026-07-24-A13-ADAPTED-FINITE-CHAOS-TRANSFER",
    "NG-2026-07-24-A13-L2-ONLY-PREDICTABLE-RECOVERY",
]
EXPECTED_OUTPUTS = {
    "primary_output": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-24-primary-principal-taylor-oneform-graph-recovery/result.json",
    "independent_output": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-24-independent-principal-taylor-oneform-graph-recovery/result.json",
    "integrated_output": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-24-integrated-principal-taylor-oneform-graph-recovery/result.json",
}
EXPECTED_SOURCES = {
    "primary": "codes/foundations/a13_classii_principal_taylor_oneform_graph_recovery.py",
    "independent": "codes/foundations/a13_classii_principal_taylor_oneform_graph_recovery_independent.py",
    "verifier": "codes/foundations/a13_classii_principal_taylor_oneform_graph_recovery_verify.py",
    "proof_note": "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/notes/classii-invariant-current-principal-oneform-graph-recovery-260724-v1.0.tex.txt",
}
LEGACY_INTEGRATED_VERDICTS = {
    "tect/a13-classii-balanced-coefficient-jet-continuum/1.0":
        "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INTEGRATED-PASS",
}


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


def strictly_decreasing(values: list[float]) -> bool:
    return all(right < left for left, right in zip(values, values[1:]))


def prior_integrated_pass(
    manifest_path: Path,
    expected_result_path: str,
    expected_result_sha256: str,
) -> tuple[bool, dict[str, Any]]:
    """Normalize the legacy and modern integrated-result contracts used here."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = manifest.get("verification") or manifest.get("run_contract")

    if isinstance(contract, dict) and "integrated_output" in contract:
        result_path = REPO / contract["integrated_output"]
        result_hash = digest(result_path)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        rows = result.get("assertions", result.get("cross_assertions", []))
        integrated_expected = int(
            contract.get("integrated_assertions", contract.get("integrated_own_assertions", -1))
        )
        aggregate_expected = int(
            contract.get("aggregate_assertions", contract.get("expected_total_assertions", -1))
        )
        summary = result.get("summary", {})
        if "pass" in result:
            pass_signal = result.get("pass") is True
        else:
            exact_legacy_verdict = LEGACY_INTEGRATED_VERDICTS.get(manifest.get("schema"))
            pass_signal = (
                exact_legacy_verdict is not None
                and
                isinstance(summary, dict)
                and int(summary.get("failed", -1)) == 0
                and result.get("verdict") == exact_legacy_verdict
            )
        assertion_count = result.get("assertion_count", len(rows))
        aggregate_count = result.get(
            "aggregate_assertion_count",
            result.get("aggregate_assertions", summary.get("total")),
        )
        passed = (
            pass_signal
            and str(result_path.relative_to(REPO)).replace("\\", "/") == expected_result_path
            and result_hash == expected_result_sha256
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
            "result_sha256": result_hash,
            "pass_signal": pass_signal,
            "result_id": result.get("result_id"),
            "manifest_sha256": result.get("manifest_sha256"),
            "assertion_count": assertion_count,
            "aggregate": aggregate_count,
        }

    if manifest.get("schema") == "tect/a6-classii-k-composite/1.0":
        result_path = manifest_path.parent / "runs/2026-07-20-integrated-k-composite/result.json"
        result_hash = digest(result_path)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        rows = result.get("assertions", [])
        summary = result.get("assertion_summary", {})
        source_reports = result.get("source_reports", {})
        passed = (
            result.get("verdict") == "A6-CLASSII-K-COMPOSITE-INTEGRATED-PASS"
            and str(result_path.relative_to(REPO)).replace("\\", "/") == expected_result_path
            and result_hash == expected_result_sha256
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
            "result_sha256": result_hash,
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
            "schema": "tect/a13-principal-taylor-oneform-graph-recovery-integrated/1.0",
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
            "aggregate_assertion_count": (
                primary_expected + independent_expected + len(rows) if passed else None
            ),
            "count_contract": {
                "primary": primary_expected,
                "independent": independent_expected,
                "integrated": integrated_expected,
                "aggregate": aggregate_expected,
            },
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
        print(
            f"AGGREGATE {primary_expected + independent_expected + len(rows)}/"
            f"{aggregate_expected} PASS"
        )
        print("A13-CLASSII-PRINCIPAL-TAYLOR-ONEFORM-GRAPH-RECOVERY-INTEGRATED-PASS")
        print(f"Evidence: {output_path}")
        return 0

    add(
        rows,
        "manifest_schema",
        manifest.get("schema")
        == "tect/a13-invariant-current-principal-oneform-graph-recovery/1.0",
        manifest.get("schema"),
        "tect/a13-invariant-current-principal-oneform-graph-recovery/1.0",
    )
    manifest_identity = {
        "result_id": manifest.get("result_id"),
        "claim": manifest.get("claim"),
        "tier": manifest.get("tier"),
        "successor_gate": manifest.get("successor_gate"),
        "source_paths": {key: record.get("path") for key, record in manifest.get("sources", {}).items()},
    }
    expected_identity = {
        "result_id": EXPECTED_RESULT,
        "claim": EXPECTED_CLAIM,
        "tier": "T4",
        "successor_gate": EXPECTED_SUCCESSOR,
        "source_paths": EXPECTED_SOURCES,
    }
    add(rows, "manifest_result", manifest_identity == expected_identity, manifest_identity, expected_identity)
    manifest_contract = {
        "result_ledger_id": manifest.get("result_ledger_id"),
        "negative_results": manifest.get("negative_results"),
        "outputs": {key: contract.get(key) for key in EXPECTED_OUTPUTS},
        "manifest_path": str(manifest_path.resolve()),
        "output_path": str(output_path.resolve()),
    }
    expected_contract = {
        "result_ledger_id": "R-075",
        "negative_results": EXPECTED_NEGATIVES,
        "outputs": EXPECTED_OUTPUTS,
        "manifest_path": str(DEFAULT_MANIFEST.resolve()),
        "output_path": str((REPO / EXPECTED_OUTPUTS["integrated_output"]).resolve()),
    }
    add(rows, "manifest_ledger", manifest_contract == expected_contract, manifest_contract, expected_contract)
    for group in ("authority", "sources"):
        for key, record in manifest[group].items():
            path = REPO / record["path"]
            actual = digest(path)
            add(rows, f"hash_{group}_{key}", actual == record["sha256"], actual, record["sha256"])
    required_runtime_authorities = {"r072_runtime_manifest", "r072_runtime_source"}
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
    add(rows, "pdf_signature", pdf_path.read_bytes().startswith(b"%PDF-"), pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    reader = PdfReader(str(pdf_path))
    add(rows, "pdf_pages", len(reader.pages) == int(pdf_record["pages"]), len(reader.pages), pdf_record["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == int(pdf_record["size_bytes"]), pdf_path.stat().st_size, pdf_record["size_bytes"])
    add(
        rows,
        "pdf_form_overfull",
        pdf_record.get("form_check") == "PASS"
        and int(pdf_record.get("overfull_hboxes", -1)) == 0,
        {"form": pdf_record.get("form_check"), "overfull": pdf_record.get("overfull_hboxes")},
        {"form": "PASS", "overfull": 0},
    )
    add(rows, "pdf_visual_qa", str(pdf_record.get("visual_qa", "")).startswith("PASS"), pdf_record.get("visual_qa"), "PASS prefix")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = has_tokens(
        note_path,
        [
            "projector-free invariant",
            "principal unshifted Taylor one-form",
            "The coefficient-transport boundary",
            "Predictable fixed-cutoff graph recovery",
            "A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER",
            "Still open",
        ],
    )
    add(rows, "note_scope_tokens", note_ok, note_missing, [])
    primary_path = REPO / manifest["sources"]["primary"]["path"]
    independent_path = REPO / manifest["sources"]["independent"]["path"]
    primary_ok, primary_missing = has_tokens(
        primary_path,
        [
            "invariant_quotient_chart",
            "constant_control_omission",
            "radial_transport_oracle",
            "adapted_infinite_chaos",
            "graph_recovery",
        ],
    )
    add(rows, "primary_scope_tokens", primary_ok, primary_missing, [])
    independent_ok, independent_missing = has_tokens(
        independent_path,
        ["complex_frames", "resonance", "omission", "radial_tail", "hermite", "graph"],
    )
    add(rows, "independent_scope_tokens", independent_ok, independent_missing, [])
    forbidden = [
        name
        for name in imported_modules(independent_path)
        if "a13_classii" in name or "a6_classii" in name or "research" in name
    ]
    add(rows, "independent_non_importing", not forbidden, forbidden, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("hash_pdf_and_scope_preflight", False)

    prior_runs: dict[str, str] = {}
    for key in ("r050_manifest", "r063_manifest", "r071_manifest", "r073_manifest", "r074_manifest"):
        prior_path = REPO / manifest["authority"][key]["path"]
        prior_record = manifest["authority"][key]
        prior_pass, details = prior_integrated_pass(
            prior_path,
            str(prior_record.get("integrated_result_path", "")),
            str(prior_record.get("integrated_result_sha256", "")),
        )
        prior_runs[key] = str(details.get("result", "missing"))
        add(rows, f"prior_{key}_integrated_contract", prior_pass, details, "hash-pinned integrated PASS")
    if not all(row["status"] == "PASS" for row in rows):
        return finish("prior_result_contracts", False, prior_runs)

    repository_checks = (
        ("results_ledger_r075", REPO / "RESULTS-LEDGER.md", ["R-075", "principal Taylor"]),
        ("claim_card_result", CLAIM_DIR / "claim.md", [EXPECTED_RESULT, "R-075"]),
        ("status_result", CLAIM_DIR / "status.json", [EXPECTED_RESULT, "R-075"]),
        ("negative_transport", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-ABSOLUTE-THIRD-ORDER-TRANSPORT"]),
        ("negative_oneform", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-ONEFORM-ONLY-ENDPOINT-OMISSION"]),
        ("negative_chaos", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-ADAPTED-FINITE-CHAOS-TRANSFER"]),
        ("negative_recovery", REPO / "negative-results/registry.md", ["NG-2026-07-24-A13-L2-ONLY-PREDICTABLE-RECOVERY"]),
        ("evidence_map", REPO / "theory/proof-evidence-map.md", ["R-075", EXPECTED_RESULT]),
        ("sector_map", REPO / "governance/sector-a-theorem-map.json", ["R-075", "A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER"]),
        ("exploration_log", REPO / "explorations/log.jsonl", ["EXP-000038", "EXP-000045"]),
        ("roadmap_successor", REPO / "ROADMAP.md", ["A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER"]),
        ("todo_successor", REPO / "TODO.md", ["A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER"]),
        ("gate_successor", REPO / "claims/GATES.md", ["A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER", "R-075"]),
    )
    for name, path, tokens in repository_checks:
        ok, missing = has_tokens(path, tokens)
        add(rows, name, ok, missing, [])
    if not all(row["status"] == "PASS" for row in rows):
        return finish("repository_integration_preflight", False, prior_runs)

    primary_process = execute(primary_path)
    independent_process = execute(independent_path)
    add(rows, "primary_exit", primary_process.returncode == 0, primary_process.returncode, 0)
    add(rows, "primary_sentinel", "A13 PRINCIPAL TAYLOR/GRAPH PRIMARY: PASS 36/36" in primary_process.stdout, primary_process.stdout[-700:], "primary PASS sentinel")
    add(rows, "independent_exit", independent_process.returncode == 0, independent_process.returncode, 0)
    add(rows, "independent_sentinel", "A13 PRINCIPAL TAYLOR/GRAPH INDEPENDENT: PASS 20/20" in independent_process.stdout, independent_process.stdout[-700:], "independent PASS sentinel")
    if not all(row["status"] == "PASS" for row in rows):
        return finish(
            "child_execution",
            False,
            {
                **prior_runs,
                "primary": primary_process.stdout + primary_process.stderr,
                "independent": independent_process.stdout + independent_process.stderr,
            },
        )

    primary_result_path = REPO / contract["primary_output"]
    independent_result_path = REPO / contract["independent_output"]
    primary_result = json.loads(primary_result_path.read_text(encoding="utf-8"))
    independent_result = json.loads(independent_result_path.read_text(encoding="utf-8"))
    primary_contract = {
        "pass": primary_result.get("pass"),
        "schema": primary_result.get("schema"),
        "result_id": primary_result.get("result_id"),
        "claim": primary_result.get("claim"),
        "run_kind": primary_result.get("run_kind"),
        "source_path": primary_result.get("source", {}).get("path"),
        "source_version": primary_result.get("source", {}).get("version"),
        "summary_status": primary_result.get("summary", {}).get("status"),
        "summary_total": primary_result.get("summary", {}).get("total"),
    }
    expected_primary_contract = {
        "pass": True,
        "schema": "tect/a13-principal-taylor-oneform-graph-recovery-run/1.0",
        "result_id": EXPECTED_RESULT,
        "claim": EXPECTED_CLAIM,
        "run_kind": "primary",
        "source_path": EXPECTED_SOURCES["primary"],
        "source_version": manifest["sources"]["primary"].get("version"),
        "summary_status": "PASS",
        "summary_total": primary_expected,
    }
    independent_contract = {
        "pass": independent_result.get("pass"),
        "schema": independent_result.get("schema"),
        "result_id": independent_result.get("result_id"),
        "claim": independent_result.get("claim"),
        "run_kind": independent_result.get("run_kind"),
        "source_path": independent_result.get("source", {}).get("path"),
        "source_version": independent_result.get("source", {}).get("version"),
        "summary_status": independent_result.get("summary", {}).get("status"),
        "summary_total": independent_result.get("summary", {}).get("total"),
    }
    expected_independent_contract = {
        "pass": True,
        "schema": "tect/a13-principal-taylor-oneform-graph-recovery-independent-run/1.0",
        "result_id": EXPECTED_RESULT,
        "claim": EXPECTED_CLAIM,
        "run_kind": "independent",
        "source_path": EXPECTED_SOURCES["independent"],
        "source_version": manifest["sources"]["independent"].get("version"),
        "summary_status": "PASS",
        "summary_total": independent_expected,
    }
    add(rows, "primary_result_pass", primary_contract == expected_primary_contract, primary_contract, expected_primary_contract)
    add(rows, "independent_result_pass", independent_contract == expected_independent_contract, independent_contract, expected_independent_contract)
    add(rows, "primary_count", primary_result.get("assertion_count") == primary_expected, primary_result.get("assertion_count"), primary_expected)
    add(rows, "independent_count", independent_result.get("assertion_count") == independent_expected, independent_result.get("assertion_count"), independent_expected)
    add(rows, "primary_source_hash_selfcheck", primary_result["source"]["sha256"] == digest(primary_path), primary_result["source"]["sha256"], digest(primary_path))
    add(rows, "independent_source_hash_selfcheck", independent_result["source"]["sha256"] == digest(independent_path), independent_result["source"]["sha256"], digest(independent_path))
    add(rows, "primary_rows_all_pass", len(primary_result["assertions"]) == primary_expected and all(row["status"] == "PASS" for row in primary_result["assertions"]), len(primary_result["assertions"]), primary_expected)
    add(rows, "independent_rows_all_pass", len(independent_result["assertions"]) == independent_expected and all(row["status"] == "PASS" for row in independent_result["assertions"]), len(independent_result["assertions"]), independent_expected)

    p = primary_result["derived"]
    i = independent_result["derived"]
    pq = p["invariant_quotient_chart"]["diagonal_coefficients"]
    iq = i["quotient"]
    add(rows, "cross_quotient_alpha", abs(float(pq["alpha"]) - float(iq["alpha"])) < 1.0e-14 and abs(float(pq["alpha"]) - 5.0 / 9.0) < 1.0e-14, [pq["alpha"], iq["alpha"]], "both 5/9")
    add(rows, "cross_Nelson_q", abs(float(pq["two_alpha"]) - float(iq["q"])) < 1.0e-14 and abs(float(iq["q"]) - 10.0 / 9.0) < 1.0e-14, [pq["two_alpha"], iq["q"]], "both 10/9")
    add(rows, "cross_quotient_diagonal_coefficients", max(abs(float(pq[key]) - float(iq[key])) for key in ("c0", "c1")) < 1.0e-14, {"primary": pq, "independent": iq}, "c0,c1 difference<1e-14")
    add(rows, "cross_tip_rank_boundary", p["invariant_quotient_chart"]["pure_singlet_frame_rank"] == iq["pure_singlet_frame_rank"] == 0 and p["invariant_quotient_chart"]["pure_singlet_invariant_rank"] == iq["pure_singlet_invariant_rank"] == 1, {"primary": [p["invariant_quotient_chart"]["pure_singlet_frame_rank"], p["invariant_quotient_chart"]["pure_singlet_invariant_rank"]], "independent": [iq["pure_singlet_frame_rank"], iq["pure_singlet_invariant_rank"]]}, "both 0 versus 1")
    independent_resonance = i["resonance"]["rows"][-1]
    add(rows, "cross_full_resonance", abs(float(p["resonance_reassembly"]["expected_full"]) - float(independent_resonance["full"])) < 2.0e-7 and float(independent_resonance["full"]) > 0.0, [p["resonance_reassembly"]["expected_full"], independent_resonance["full"]], "independent stencil difference<2e-7 and positive")
    add(rows, "cross_isolated_resonance", abs(float(p["resonance_reassembly"]["expected_isolated"]) - float(independent_resonance["isolated"])) < 2.0e-7 and float(independent_resonance["isolated"]) < 0.0, [p["resonance_reassembly"]["expected_isolated"], independent_resonance["isolated"]], "independent stencil difference<2e-7 and negative")
    add(rows, "cross_omission_raw_remainder", abs(float(p["constant_control_omission"]["raw_taylor_remainder"]) - float(i["omission"]["raw_remainder"])) < 3.0e-13 and float(i["omission"]["raw_remainder"]) < 0.0, [p["constant_control_omission"]["raw_taylor_remainder"], i["omission"]["raw_remainder"]], "difference<3e-13 and negative")
    add(rows, "cross_omission_square", abs(float(p["constant_control_omission"]["retained_square"]) - float(i["omission"]["square"])) < 3.0e-13 and float(i["omission"]["square"]) > 0.0, [p["constant_control_omission"]["retained_square"], i["omission"]["square"]], "difference<3e-13 and positive")
    add(rows, "cross_omission_curvature", abs(float(p["constant_control_omission"]["coefficient_curvature_pair"]) - float(i["omission"]["curvature"])) < 3.0e-13 and abs(float(i["omission"]["curvature"])) > float(i["omission"]["square"]), [p["constant_control_omission"]["coefficient_curvature_pair"], i["omission"]["curvature"]], "difference<3e-13 and dominates square")
    radial_target = float(p["radial_transport_oracle"]["expected_transport_contraction"])
    radial_measured = float(i["radial_tail"]["value"])
    radial_relative_error = abs(radial_target - radial_measured) / abs(radial_target)
    add(rows, "cross_horizontal_radial_tail", radial_relative_error < 2.0e-4 and radial_measured > 0.0, {"primary_analytic": radial_target, "independent_measured": radial_measured, "relative_error": radial_relative_error}, "independent value positive with relative error<2e-4")
    shared_orders = [str(order) for order in range(0, 18, 2)]
    hermite_error = max(abs(float(p["adapted_infinite_chaos"]["coefficients"][order]) - float(i["hermite"]["quadratures"]["128"][order])) for order in shared_orders)
    add(rows, "cross_Hermite_coefficients", hermite_error < 2.0e-10, hermite_error, "independent quadrature error<2e-10")
    add(rows, "cross_adapted_infinite_chaos", i["hermite"]["all_nonzero"] is True and all(float(p["adapted_infinite_chaos"]["coefficients"][order]) != 0.0 for order in shared_orders), {"independent_all_nonzero": i["hermite"]["all_nonzero"], "orders": shared_orders}, "all tested even orders nonzero")
    graph_ok = all(strictly_decreasing([float(value) for value in p["graph_recovery"][key]]) for key in ("H2_errors", "L6_errors", "current_errors")) and all(strictly_decreasing([float(value) for value in i["graph"][key]]) for key in ("H2", "L6", "current"))
    add(rows, "cross_graph_recovery_decreases", graph_ok, {"primary": p["graph_recovery"], "independent": i["graph"]}, "all H2, L6, and current errors strictly decrease")
    add(rows, "cross_principal_Young_slack", abs(float(p["budget"]["principal"]["young_slack"]) - float(i["principal_slack"])) < 1.0e-15 and float(i["principal_slack"]) > 0.0, [p["budget"]["principal"]["young_slack"], i["principal_slack"]], "equal and positive")
    add(rows, "cross_transport_criticality", abs(float(p["budget"]["transport"]["young_slack"]) - float(i["transport_slack"])) < 1.0e-15 and float(i["transport_slack"]) == 0.0, [p["budget"]["transport"]["young_slack"], i["transport_slack"]], "both zero")
    p_spike = p["budget"]["predictable_L2_counterexample"]
    i_spike = i["predictable_spike"]
    add(rows, "cross_L2_only_spike", float(p_spike[-1]["L2_energy"]) < float(p_spike[0]["L2_energy"]) and float(i_spike[-1]["L2"]) < float(i_spike[0]["L2"]) and max(abs(float(row["terminal_L6_sixth"]) - 1.0) for row in p_spike) < 2.0e-15 and max(abs(float(row["L6_sixth"]) - 1.0) for row in i_spike) < 2.0e-15, {"primary": p_spike, "independent": i_spike}, "L2 decreases while terminal L6 sixth remains one")
    add(rows, "scope_firewall_keeps_signed_transport_open", "remain open" in primary_result["honesty_boundary"] and "remain open" in independent_result["honesty_boundary"] and "remain open" in manifest["honesty_boundary"], [primary_result["honesty_boundary"], independent_result["honesty_boundary"], manifest["honesty_boundary"]], "explicit open boundary in all three")

    add(rows, "integrated_count_contract", len(rows) + 2 == integrated_expected, len(rows) + 2, integrated_expected)
    aggregate_actual = primary_expected + independent_expected + len(rows) + 1
    add(rows, "aggregate_count_contract", aggregate_actual == aggregate_expected, aggregate_actual, aggregate_expected)
    passed = all(row["status"] == "PASS" for row in rows)
    child_runs = {
        **prior_runs,
        "primary": str(primary_result_path.relative_to(REPO)).replace("\\", "/"),
        "independent": str(independent_result_path.relative_to(REPO)).replace("\\", "/"),
    }
    return finish("complete", passed, child_runs)


if __name__ == "__main__":
    raise SystemExit(run())
