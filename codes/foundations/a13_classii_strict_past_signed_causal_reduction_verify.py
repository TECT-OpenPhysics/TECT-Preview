#!/usr/bin/env python3
"""Integrated verifier for the A13 strict-past signed causal reduction."""

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
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_strict_past_signed_causal_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-23-integrated-strict-past-signed-causal-reduction" / "result.json"


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
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def execute(script: Path) -> None:
    completed = subprocess.run([sys.executable, str(script)], cwd=REPO, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run(manifest_path: Path, output_path: Path, reuse: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    if not reuse or not primary_output.exists():
        execute(primary_script)
    if not reuse or not independent_output.exists():
        execute(independent_script)
    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, source in manifest["sources"].items():
        actual = digest(REPO / source["path"])
        add(rows, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(rows, "independent_pass", independent.get("pass") is True, independent.get("pass"), True)
    add(rows, "primary_assertion_contract", primary.get("assertion_count") == 12, primary.get("assertion_count"), 12)
    add(rows, "independent_assertion_contract", independent.get("assertion_count") == 11, independent.get("assertion_count"), 11)
    add(rows, "shared_result_id", primary.get("result_id") == independent.get("result_id") == manifest["result_id"], [primary.get("result_id"), independent.get("result_id")], manifest["result_id"])
    p = primary["computed"]
    i = independent["computed"]
    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    add(rows, "cross_completion_gap", abs(float(p["completion_gap"]) - float(i["completion_gap"])) < tolerance, [p["completion_gap"], i["completion_gap"]], f"difference<{tolerance}")
    add(rows, "both_causal_residuals_close", max(float(p["identity_residual"]), float(i["causal_identity_residual"])) < tolerance, [p["identity_residual"], i["causal_identity_residual"]], f"maximum<{tolerance}")
    add(rows, "both_metric_resolvent_residuals_close", max(float(p["metric_completion_residual"]), float(i["metric_completion_residual"])) < tolerance, [p["metric_completion_residual"], i["metric_completion_residual"]], f"maximum<{tolerance}")
    add(rows, "cross_q_equals_ten_ninths", abs(float(p["q_from_epsilon"]) - 10.0 / 9.0) < tolerance and abs(float(i["q_from_epsilon"]) - 10.0 / 9.0) < tolerance, [p["q_from_epsilon"], i["q_from_epsilon"]], 10.0 / 9.0)
    add(rows, "expectation_not_pointwise_control", bool(primary["assertions"]["completion_is_expectation_only_not_pointwise"]) and float(p["min_pointwise_gap"]) < 0, p["min_pointwise_gap"], "negative witness")
    minimum = float(manifest["independent_audit"]["negative_control_minimum"])
    add(rows, "noncausal_shift_negative_control", float(i["bad_shift_residual"]) > minimum, i["bad_shift_residual"], f">{minimum}")
    add(rows, "future_predictor_negative_control", float(i["bad_predictor_residual"]) > minimum, i["bad_predictor_residual"], f">{minimum}")

    note_text = (REPO / manifest["sources"]["proof_note"]["path"]).read_text(encoding="utf-8")
    tokens = (
        "A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION",
        "A13-CLASSII-STRICT-PAST-SIGNED-Q-CURRENT-FORM-BOUND",
        "\\mathfrak S_{J,q}",
        "{10\\over9}",
        "expectation identity",
        "Exact A11 production signed charge",
        "Devil's-advocate",
        "Result footer",
    )
    add(rows, "proof_note_required_content", all(token in note_text for token in tokens), [token for token in tokens if token not in note_text], [])
    pdf = manifest["proof_pdf"]
    pdf_path = REPO / pdf["path"]
    add(rows, "proof_pdf_hash", digest(pdf_path) == pdf["sha256"], digest(pdf_path), pdf["sha256"])
    add(rows, "proof_pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    add(rows, "proof_pdf_size", pdf_path.stat().st_size == pdf["size_bytes"], pdf_path.stat().st_size, pdf["size_bytes"])
    add(rows, "proof_pdf_qa", pdf["pages"] > 0 and pdf["form_check"] == "PASS" and pdf["overfull_hbox_count"] == 0 and pdf["visual_qa"] in {"PASS", "AUTOMATED-RENDER-PASS"}, pdf, "closed QA")

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    result_id = manifest["result_id"]
    next_gate = manifest["consequence"]["next_subgate"]
    umbrella = manifest["consequence"]["umbrella_gate"]
    add(rows, "status_t4_and_umbrella_open", status.get("tier") == "T4" and status.get("open_gates") == [umbrella], [status.get("tier"), status.get("open_gates")], ["T4", [umbrella]])
    add(rows, "status_records_reduction_and_next", result_id in status.get("statement", "") and next_gate in status.get("next_action", ""), [result_id in status.get("statement", ""), next_gate in status.get("next_action", "")], [True, True])
    add(rows, "claim_records_honesty_boundary", result_id in claim_text and next_gate in claim_text and "pointwise" in claim_text.lower(), [result_id in claim_text, next_gate in claim_text, "pointwise" in claim_text.lower()], [True, True, True])
    add(rows, "gates_record_scoped_advance", result_id in gates_text and "SIGNED-CHARGE" in gates_text, [result_id in gates_text, "SIGNED-CHARGE" in gates_text], [True, True])
    add(rows, "roadmap_records_reduction", result_id in roadmap_text and next_gate in roadmap_text, [result_id in roadmap_text, next_gate in roadmap_text], [True, True])
    add(rows, "todo_keeps_t050_in_progress", "**T-050**" in todo_text and result_id in todo_text and next_gate in todo_text, ["**T-050**" in todo_text, result_id in todo_text, next_gate in todo_text], [True, True, True])
    add(rows, "changelog_records_package", result_id in changelog_text, result_id in changelog_text, True)
    add(rows, "manifest_preserves_open_boundary", manifest["claims_not_established"]["production_signed_charge_bound"] is False and manifest["claims_not_established"]["one_use_bound"] is False and manifest["claims_not_established"]["nelson_bound"] is False, manifest["claims_not_established"], "all false")

    modules: list[str] = []
    for node in ast.walk(ast.parse(independent_script.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    add(rows, "independent_does_not_import_primary", "a13_classii_strict_past_signed_causal_reduction" not in modules, modules, "primary absent")

    failures = [row for row in rows if row["status"] != "PASS"]
    child_total = int(primary["assertion_count"]) + int(independent["assertion_count"])
    child_failed = 0 if primary.get("pass") and independent.get("pass") else child_total
    total = child_total + len(rows)
    failed = child_failed + len(failures)
    payload = {
        "schema": "tect/a13-strict-past-resolvent-signed-charge-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": result_id,
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "primary": primary,
        "independent": independent,
        "integrated_assertions": rows,
        "summary": {"passed": total - failed, "total": total, "failed": failed},
        "verdict": "A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION-INTEGRATED-PASS" if not failures and failed == 0 else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures or failed:
        print(f"FAIL: integrated ({failed} total failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {total}/{total}")
    print("A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION-INTEGRATED-PASS")
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
