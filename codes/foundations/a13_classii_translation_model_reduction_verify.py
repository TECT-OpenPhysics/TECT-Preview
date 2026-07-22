#!/usr/bin/env python3
"""One-command verifier for the A13 Class-II translation/model reduction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_translation_model_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-integrated-translation-model-reduction" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def execute(script: Path, manifest: Path, output: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def rows_by_cutoff(payload: dict[str, Any], key: str) -> dict[int, dict[str, Any]]:
    return {
        int(row["cutoff"]): row
        for row in payload["derived"]["homogeneous_remainder_nogo"]["rows"]
        if key in row
    }


def run(manifest_path: Path, output_path: Path, reuse: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    if not reuse or not primary_output.exists():
        execute(primary_script, manifest_path, primary_output)
    if not reuse or not independent_output.exists():
        execute(independent_script, manifest_path, independent_output)

    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, source in manifest["sources"].items():
        actual = digest(REPO / source["path"])
        add(rows, f"integrated_source_{key}_hash", actual == source["sha256"], actual, source["sha256"])
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"integrated_authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    current_manifest_hash = digest(manifest_path)
    primary_summary = primary.get("summary", {})
    independent_summary = independent.get("summary", {})
    add(rows, "primary_manifest_hash", primary.get("manifest_sha256") == current_manifest_hash, primary.get("manifest_sha256"), current_manifest_hash)
    add(rows, "independent_manifest_hash", independent.get("manifest_sha256") == current_manifest_hash, independent.get("manifest_sha256"), current_manifest_hash)
    add(rows, "primary_assertion_contract", primary_summary.get("total") == manifest["run_contract"]["primary_assertions"], primary_summary, manifest["run_contract"]["primary_assertions"])
    add(rows, "independent_assertion_contract", independent_summary.get("total") == manifest["run_contract"]["independent_assertions"], independent_summary, manifest["run_contract"]["independent_assertions"])
    add(rows, "primary_all_pass", primary_summary.get("failed") == 0, primary_summary, "failed=0")
    add(rows, "independent_all_pass", independent_summary.get("failed") == 0, independent_summary, "failed=0")

    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    for key in ("a", "b", "c"):
        p_value = float(primary["derived"]["coefficients"][key])
        i_value = float(independent["derived"]["coefficients"][key])
        add(rows, f"cross_coefficient_{key}", abs(p_value - i_value) < tolerance, [p_value, i_value], f"difference<{tolerance}")
    for p_key, i_key in (
        ("critical_density", "critical_density"),
        ("constant_density", "constant_density"),
        ("final_sextic_margin", "retained_margin"),
        ("sharp_one_use_upper", "sharp_upper"),
    ):
        p_value = float(primary["derived"]["potential"][p_key])
        i_value = float(independent["derived"]["potential"][i_key])
        add(rows, f"cross_potential_{p_key}", abs(p_value - i_value) < tolerance, [p_value, i_value], f"difference<{tolerance}")
    add(rows, "both_translation_routes_machine_close", primary["derived"]["translation"]["maximum_tensor_error"] < manifest["audit"]["translation_tolerance"] and independent["derived"]["translation"]["maximum_endpoint_error"] < manifest["independent_audit"]["translation_tolerance"], [primary["derived"]["translation"]["maximum_tensor_error"], independent["derived"]["translation"]["maximum_endpoint_error"]], "both below route tolerances")
    add(rows, "cartan_identity_closed", primary["derived"]["cartan"]["maximum_error"] < manifest["audit"]["cartan_tolerance"], primary["derived"]["cartan"]["maximum_error"], manifest["audit"]["cartan_tolerance"])
    add(rows, "both_deterministic_expectation_routes_close", primary["derived"]["deterministic_expectation"]["maximum_identity_error"] < manifest["audit"]["expectation_tolerance"] and independent["derived"]["deterministic_expectation"]["translation_error"] < manifest["independent_audit"]["expectation_tolerance"], [primary["derived"]["deterministic_expectation"]["maximum_identity_error"], independent["derived"]["deterministic_expectation"]["translation_error"]], "both below route tolerances")

    primary_cutoffs = rows_by_cutoff(primary, "required_deterministic_remainder")
    independent_cutoffs = rows_by_cutoff(independent, "required_remainder")
    shared = sorted(set(primary_cutoffs) & set(independent_cutoffs))
    add(rows, "homogeneous_nogo_has_shared_cutoffs", len(shared) >= 3, shared, "at least three")
    for cutoff in shared:
        p_value = float(primary_cutoffs[cutoff]["required_deterministic_remainder"])
        i_value = float(independent_cutoffs[cutoff]["required_remainder"])
        relative = abs(p_value - i_value) / max(1.0, abs(p_value), abs(i_value))
        add(rows, f"cross_homogeneous_deficit_J{cutoff}", relative < float(manifest["integrated_audit"]["homogeneous_relative_tolerance"]), [p_value, i_value, relative], f"relative<{manifest['integrated_audit']['homogeneous_relative_tolerance']}")
    add(rows, "both_nogo_routes_show_superlinear_growth", primary["derived"]["homogeneous_remainder_nogo"]["log_log_growth_slope"] > manifest["audit"]["homogeneous_growth_slope_lower"] and independent["derived"]["homogeneous_remainder_nogo"]["growth_slope"] > manifest["independent_audit"]["homogeneous_growth_slope_lower"], [primary["derived"]["homogeneous_remainder_nogo"]["log_log_growth_slope"], independent["derived"]["homogeneous_remainder_nogo"]["growth_slope"]], "both above thresholds")
    add(rows, "both_routes_identify_moment_gap", primary["derived"]["model_lift_arithmetic"]["required_q_model_moment"] > 2.0 and independent["derived"]["required_q_model_moment"] > 2.0, [primary["derived"]["model_lift_arithmetic"]["required_q_model_moment"], independent["derived"]["required_q_model_moment"]], ">2")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_text = note_path.read_text(encoding="utf-8")
    required_note_tokens = (
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
        "A13-CLASSII-CAMERON-MARTIN-TRANSLATED-CURRENT-MODEL-LIFT",
        "AUDIT-2026-07-22-A13-HALF-SEXTIC-OVERRESTRICTION",
        "gamma/6",
        "epsilon_6=0.15",
        "R_J^*",
        "does not prove the cutoff-uniform Nelson moment",
        "Cartan",
        "L^3",
        "deterministic constant remainder",
    )
    add(rows, "proof_note_required_content", all(token in note_text for token in required_note_tokens), [token for token in required_note_tokens if token not in note_text], [])

    pdf = manifest["proof_pdf"]
    pdf_path = REPO / pdf["path"]
    add(rows, "proof_pdf_hash", digest(pdf_path) == pdf["sha256"], digest(pdf_path), pdf["sha256"])
    add(rows, "proof_pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    add(rows, "proof_pdf_size", pdf_path.stat().st_size == pdf["size_bytes"], pdf_path.stat().st_size, pdf["size_bytes"])
    add(rows, "proof_pdf_qa", pdf["pages"] > 0 and pdf["form_check"] == "PASS" and pdf["overfull_hbox_count"] == 0 and pdf["visual_qa"] == "PASS", pdf, "closed QA")

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    registry_text = (REPO / "negative-results" / "registry.md").read_text(encoding="utf-8")
    umbrella = manifest["consequence"]["umbrella_gate"]
    next_subgate = manifest["consequence"]["next_subgate"]
    add(rows, "status_remains_t4_active", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", [status.get("tier"), status.get("lifecycle")], ["T4", "ACTIVE"])
    add(rows, "status_preserves_single_umbrella_gate", status.get("open_gates") == [umbrella], status.get("open_gates"), [umbrella])
    add(rows, "status_names_model_lift_next", next_subgate in status.get("next_action", ""), status.get("next_action"), next_subgate)
    add(rows, "status_no_overclaim_updated", "does not prove" in status.get("no_overclaim", "").lower() and "T5" in status.get("no_overclaim", ""), status.get("no_overclaim"), "explicit Nelson and tier exclusions")
    claim_lower = claim_text.lower()
    add(rows, "claim_records_exact_translation_reduction", "exact finite-cutoff translation" in claim_lower and next_subgate in claim_text, ["exact finite-cutoff translation" in claim_lower, next_subgate in claim_text], [True, True])
    add(rows, "gates_records_model_lift", next_subgate in gates_text and umbrella in gates_text, [next_subgate in gates_text, umbrella in gates_text], [True, True])
    add(rows, "roadmap_records_model_lift", next_subgate in roadmap_text and "L^3" in roadmap_text, [next_subgate in roadmap_text, "L^3" in roadmap_text], [True, True])
    add(rows, "todo_keeps_t050_in_progress", "**T-050**" in todo_text and next_subgate in todo_text and "In progress" in todo_text, ["**T-050**" in todo_text, next_subgate in todo_text], [True, True, True])
    add(rows, "results_registers_r060", "R-060" in results_text and manifest["result_id"] in results_text, ["R-060" in results_text, manifest["result_id"] in results_text], [True, True])
    add(rows, "registry_records_half_sextic_audit", "AUDIT-2026-07-22-A13-HALF-SEXTIC-OVERRESTRICTION" in registry_text, "audit token", "present")
    add(rows, "registry_preserves_ramer_determinant_nogo", "NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT" in registry_text and "determinant" in registry_text.lower(), "Ramer determinant language", "present")

    independent_text = independent_script.read_text(encoding="utf-8")
    imported_modules = []
    for node in ast.walk(ast.parse(independent_text)):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    add(
        rows,
        "independent_does_not_import_primary",
        "a13_classii_translation_model_reduction" not in imported_modules,
        imported_modules,
        "primary module absent",
    )
    add(rows, "v1_1_manifest_preserved", digest(REPO / manifest["authority"]["a13_v1_1_manifest"]["path"]) == manifest["authority"]["a13_v1_1_manifest"]["sha256"], digest(REPO / manifest["authority"]["a13_v1_1_manifest"]["path"]), manifest["authority"]["a13_v1_1_manifest"]["sha256"])
    add(rows, "v1_1_result_preserved", digest(REPO / manifest["authority"]["a13_v1_1_integrated_result"]["path"]) == manifest["authority"]["a13_v1_1_integrated_result"]["sha256"], digest(REPO / manifest["authority"]["a13_v1_1_integrated_result"]["path"]), manifest["authority"]["a13_v1_1_integrated_result"]["sha256"])

    expected_own = int(manifest["run_contract"]["integrated_own_assertions"])
    add(rows, "integrated_own_assertion_contract", len(rows) + 2 == expected_own, len(rows) + 2, expected_own)
    failures = [row for row in rows if row["status"] != "PASS"]
    total_before_aggregate = int(primary_summary.get("total", 0)) + int(independent_summary.get("total", 0)) + len(rows)
    expected_total = int(manifest["run_contract"]["expected_total_assertions"])
    aggregate_ok = total_before_aggregate + 1 == expected_total
    aggregate = {
        "name": "aggregate_assertion_count",
        "status": "PASS" if aggregate_ok else "FAIL",
        "actual": total_before_aggregate + 1,
        "expected": expected_total,
    }
    rows.append(aggregate)
    if not aggregate_ok:
        failures.append(aggregate)
    own_failed = len([row for row in rows if row["status"] != "PASS"])
    child_failed = int(primary_summary.get("failed", 0)) + int(independent_summary.get("failed", 0))
    total_failed = child_failed + own_failed
    passed = int(primary_summary.get("passed", 0)) + int(independent_summary.get("passed", 0)) + len(rows) - own_failed
    total = int(primary_summary.get("total", 0)) + int(independent_summary.get("total", 0)) + len(rows)
    payload = {
        "schema": "tect/a13-classii-translation-model-reduction-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": current_manifest_hash,
        "primary": primary,
        "independent": independent,
        "cross_assertions": rows,
        "summary": {"passed": passed, "total": total, "failed": total_failed},
        "verdict": "A13-CLASSII-TRANSLATION-MODEL-REDUCTION-INTEGRATED-PASS" if not failures and total_failed == 0 else "FAIL",
        "consequence": manifest["consequence"],
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures or total_failed:
        print(f"FAIL: integrated ({total_failed} total failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {passed}/{total}")
    print("A13-CLASSII-TRANSLATION-MODEL-REDUCTION-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reuse", action="store_true")
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve(), arguments.reuse)


if __name__ == "__main__":
    raise SystemExit(main())
