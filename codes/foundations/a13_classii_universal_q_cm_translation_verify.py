#!/usr/bin/env python3
"""One-command verifier for the A13 universal-Q/CM translation package."""

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
DEFAULT_MANIFEST = CLAIM / "classii_universal_q_cm_translation_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-integrated-universal-q-cm-translation" / "result.json"


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


def by_cutoff(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(item["cutoff"]): item
        for item in payload["derived"]["q_majorant_fixtures"]
    }


def by_radius(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(item["radius"]): item for item in items}


def markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    next_heading = text.find("\n### ", start + len(heading))
    return text[start:] if next_heading < 0 else text[start:next_heading]


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
        path = REPO / source["path"]
        actual = digest(path)
        add(rows, f"integrated_source_{key}_hash", actual == source["sha256"], actual, source["sha256"])
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"integrated_authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    manifest_hash = digest(manifest_path)
    primary_summary = primary.get("summary", {})
    independent_summary = independent.get("summary", {})
    add(rows, "primary_manifest_hash", primary.get("manifest_sha256") == manifest_hash, primary.get("manifest_sha256"), manifest_hash)
    add(rows, "independent_manifest_hash", independent.get("manifest_sha256") == manifest_hash, independent.get("manifest_sha256"), manifest_hash)
    add(rows, "primary_assertion_contract", primary_summary.get("total") == manifest["run_contract"]["primary_assertions"], primary_summary, manifest["run_contract"]["primary_assertions"])
    add(rows, "independent_assertion_contract", independent_summary.get("total") == manifest["run_contract"]["independent_assertions"], independent_summary, manifest["run_contract"]["independent_assertions"])
    add(rows, "primary_all_pass", primary_summary.get("failed") == 0, primary_summary, "failed=0")
    add(rows, "independent_all_pass", independent_summary.get("failed") == 0, independent_summary, "failed=0")

    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    p_arithmetic = primary["derived"]["theorem_arithmetic"]
    for key, independent_key in (
        ("q_spectrum_decay", "q_spectrum_decay"),
        ("q_sobolev_ceiling", "q_sobolev_ceiling"),
        ("required_model_moment", "required_model_moment"),
    ):
        p_value = float(p_arithmetic[key])
        i_value = float(independent["derived"][independent_key])
        add(rows, f"cross_{key}", abs(p_value - i_value) < tolerance, [p_value, i_value], f"difference<{tolerance}")

    shared_cutoff = int(manifest["independent_audit"]["shared_cutoff"])
    primary_fixture = by_cutoff(primary)[shared_cutoff]
    for key, independent_value in independent["derived"]["direct_q_values"].items():
        primary_value = float(primary_fixture["selected_outputs"][key])
        independent_value = float(independent_value)
        relative = abs(primary_value - independent_value) / max(1.0, abs(primary_value), abs(independent_value))
        add(rows, f"cross_q_value_N{shared_cutoff}_{key}", relative < tolerance, [primary_value, independent_value, relative], f"relative<{tolerance}")

    add(rows, "both_translation_identities_close", primary["derived"]["translation_identity"]["maximum_error"] < manifest["audit"]["translation_tolerance"] and independent["derived"]["tensor_translation_error"] < manifest["independent_audit"]["translation_tolerance"], [primary["derived"]["translation_identity"]["maximum_error"], independent["derived"]["tensor_translation_error"]], "both below tolerances")
    p_cones = by_radius(primary["derived"]["nested_resonance_cone_certificate"])
    i_cones = by_radius(independent["derived"]["nested_resonance_cone_certificate"])
    shared_radii = sorted(set(p_cones) & set(i_cones))
    add(rows, "cone_routes_share_three_radii", len(shared_radii) >= 3, shared_radii, "at least three")
    for radius in shared_radii:
        p_value = float(p_cones[radius]["double_contraction_magnitude"])
        i_value = float(i_cones[radius]["double_contraction_magnitude"])
        relative = abs(p_value - i_value) / max(1.0, abs(p_value), abs(i_value))
        add(rows, f"cross_cone_double_contraction_magnitude_r{radius}", relative < tolerance, [p_value, i_value, relative], f"relative<{tolerance}")
    counts = independent["derived"]["contraction_counts"]
    add(rows, "scalar_pairing_count_fixture", counts == {"xq_single": 2, "xxq_double": 2, "xxq_single": 4}, counts, {"xq_single": 2, "xxq_double": 2, "xxq_single": 4})
    add(rows, "localized_first_chaos_witness_nonzero", abs(float(primary["derived"]["localized_first_chaos_witness"])) > manifest["audit"]["localized_witness_minimum"], primary["derived"]["localized_first_chaos_witness"], f"absolute>{manifest['audit']['localized_witness_minimum']}")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_text = note_path.read_text(encoding="utf-8")
    note_tokens = (
        "A13-CLASSII-UNIVERSAL-Q-ALL-MOMENTS-AND-CM-TRANSLATION",
        "A13-CLASSII-COEFFICIENT-JET-RENORMALISATION-CLASSIFICATION",
        "A13-CLASSII-CAMERON-MARTIN-TRANSLATED-CURRENT-MODEL-LIFT",
        "0<\\kappa<1/2",
        "c\\log\\Lambda",
        "cone-localized",
        "total symmetric Littlewood--Paley tree",
        "Devil's-advocate",
        "Result footer",
    )
    add(rows, "proof_note_required_content", all(token in note_text for token in note_tokens), [token for token in note_tokens if token not in note_text], [])
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
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    closed = manifest["consequence"]["closed_subgate"]
    parent = manifest["consequence"]["parent_subgate"]
    umbrella = manifest["consequence"]["umbrella_gate"]
    next_gate = manifest["consequence"]["next_subgate"]
    negative = manifest["consequence"]["negative_record"]
    parent_section = markdown_section(gates_text, f"### **{parent}**")
    closed_section = markdown_section(gates_text, f"### **{closed}**")
    next_section = markdown_section(gates_text, f"### **{next_gate}**")
    negative_section = markdown_section(registry_text, f"### {negative}")
    add(rows, "status_remains_t4_active", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", [status.get("tier"), status.get("lifecycle")], ["T4", "ACTIVE"])
    add(rows, "status_preserves_umbrella_gate_only", status.get("open_gates") == [umbrella], status.get("open_gates"), [umbrella])
    add(rows, "status_records_closed_and_next_subgates", closed in status.get("statement", "") and next_gate in status.get("next_action", ""), [closed in status.get("statement", ""), next_gate in status.get("next_action", "")], [True, True])
    add(rows, "claim_records_raw_jet_correction", closed in claim_text and next_gate in claim_text and "logarithmic" in claim_text.lower(), [closed in claim_text, next_gate in claim_text, "logarithmic" in claim_text.lower()], [True, True, True])
    add(rows, "gates_record_split", "**Status:** OPEN (universal-Q child CLOSED)" in parent_section and "**Status:** CLOSED" in closed_section and "**Status:** OPEN SELECTED SUBGATE" in next_section, ["OPEN (universal-Q child CLOSED)" in parent_section, "**Status:** CLOSED" in closed_section, "**Status:** OPEN SELECTED SUBGATE" in next_section], [True, True, True])
    add(rows, "roadmap_records_next_gate", closed in roadmap_text and next_gate in roadmap_text, [closed in roadmap_text, next_gate in roadmap_text], [True, True])
    add(rows, "todo_keeps_t050_in_progress", "**T-050**" in todo_text and closed in todo_text and next_gate in todo_text, ["**T-050**" in todo_text, closed in todo_text, next_gate in todo_text], [True, True, True])
    add(rows, "results_register_r061", "R-061" in results_text and manifest["result_id"] in results_text, ["R-061" in results_text, manifest["result_id"] in results_text], [True, True])
    add(rows, "registry_records_raw_jet_nogo", bool(negative_section) and "cone-localized" in negative_section and "total" in negative_section.lower(), [bool(negative_section), "cone-localized" in negative_section, "total" in negative_section.lower()], [True, True, True])
    add(rows, "changelog_records_package", manifest["result_id"] in changelog_text and negative in changelog_text, [manifest["result_id"] in changelog_text, negative in changelog_text], [True, True])
    add(rows, "honesty_boundary_preserves_nelson_exclusion", "does not" in manifest["honesty_boundary"].lower() and "Nelson" in manifest["honesty_boundary"] and "T5" in manifest["honesty_boundary"], manifest["honesty_boundary"], "explicit Nelson and tier exclusions")

    independent_text = independent_script.read_text(encoding="utf-8")
    imported_modules: list[str] = []
    for node in ast.walk(ast.parse(independent_text)):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    add(rows, "independent_does_not_import_primary", "a13_classii_universal_q_cm_translation" not in imported_modules, imported_modules, "primary module absent")

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
        "schema": "tect/a13-classii-universal-q-cm-translation-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": manifest_hash,
        "primary": primary,
        "independent": independent,
        "cross_assertions": rows,
        "summary": {"passed": passed, "total": total, "failed": total_failed},
        "verdict": "A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-INTEGRATED-PASS" if not failures and total_failed == 0 else "FAIL",
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
    print("A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-INTEGRATED-PASS")
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
