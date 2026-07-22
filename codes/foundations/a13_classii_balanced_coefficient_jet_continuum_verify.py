#!/usr/bin/env python3
"""One-command verifier for the A13 balanced coefficient-jet continuum package."""

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
DEFAULT_MANIFEST = CLAIM / "classii_balanced_coefficient_jet_continuum_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-integrated-balanced-coefficient-jet-continuum"
    / "result.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def execute(script: Path, manifest: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{script.name} failed ({completed.returncode})\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    end = text.find("\n### ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def run(manifest_path: Path, output_path: Path, reuse: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    if reuse and primary_output.exists():
        primary = json.loads(primary_output.read_text(encoding="utf-8"))
    else:
        primary = execute(primary_script, manifest_path, primary_output)
    if reuse and independent_output.exists():
        independent = json.loads(independent_output.read_text(encoding="utf-8"))
    else:
        independent = execute(independent_script, manifest_path, independent_output)

    rows: list[dict[str, Any]] = []
    for key, source in manifest["sources"].items():
        actual = digest(REPO / source["path"])
        add(rows, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    manifest_hash = digest(manifest_path)
    add(rows, "primary_manifest_hash", primary.get("manifest_sha256") == manifest_hash, primary.get("manifest_sha256"), manifest_hash)
    add(rows, "independent_manifest_hash", independent.get("manifest_sha256") == manifest_hash, independent.get("manifest_sha256"), manifest_hash)
    add(rows, "primary_verdict", primary.get("verdict") == "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-PRIMARY-PASS", primary.get("verdict"), "primary pass")
    add(rows, "independent_verdict", independent.get("verdict") == "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INDEPENDENT-PASS", independent.get("verdict"), "independent pass")
    add(rows, "primary_assertion_count", primary["summary"]["total"] == manifest["run_contract"]["primary_assertions"], primary["summary"], manifest["run_contract"]["primary_assertions"])
    add(rows, "independent_assertion_count", independent["summary"]["total"] == manifest["run_contract"]["independent_assertions"], independent["summary"], manifest["run_contract"]["independent_assertions"])
    add(rows, "children_zero_failures", primary["summary"]["failed"] == 0 and independent["summary"]["failed"] == 0, [primary["summary"]["failed"], independent["summary"]["failed"]], [0, 0])

    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    primary_arithmetic = primary["derived"]["theorem_arithmetic"]
    independent_arithmetic = independent["derived"]["theorem_arithmetic"]
    for key in manifest["oracles"]["theorem_arithmetic"]:
        p_value = float(primary_arithmetic[key])
        i_value = float(independent_arithmetic[key])
        add(rows, f"cross_arithmetic_{key}", abs(p_value - i_value) < tolerance, [p_value, i_value], f"difference<{tolerance}")

    sparse = primary["derived"]["balanced_sparse_fixture"]
    dense = independent["derived"]["dense_parenthesisation"]
    add(rows, "cross_parenthesisations_close", sparse["left_equals_right"] and dense["maximum_absolute_associator"] < 1.0e-9, [sparse["left_equals_right"], dense["maximum_absolute_associator"]], "both close")
    forest = primary["derived"]["forest_polynomial_fixture"]
    hermite = independent["derived"]["hermite_quadrature"]
    forest_counts = [
        float(forest["first_cross_count"]),
        float(forest["second_cross_count"]),
        float(forest["raw_second_chaos_count"]),
        float(forest["recursive_second_chaos_count"]),
    ]
    hermite_counts = [
        float(hermite["xh2_p1"]),
        float(hermite["h2h2_p2"]),
        float(hermite["x2h2_p2"]),
        float(hermite["xh3_p2"]),
    ]
    forest_count_error = max(abs(left - right) for left, right in zip(forest_counts, hermite_counts))
    add(rows, "cross_forest_2_4_5_3", forest_count_error < tolerance, [forest_counts, hermite_counts, forest_count_error], f"2,4,5,3 within {tolerance}")
    add(rows, "cross_sigma_q_retained", abs(float(forest["sigma_q"])) > 1.0e-3 and float(forest["error_if_sigma_q_deleted"]) > 1.0e-3, [forest["sigma_q"], forest["error_if_sigma_q_deleted"]], "nonzero and deletion fails")
    primary_chart = primary["derived"]["rational_reconstruction_fixture"]
    independent_chart = independent["derived"]["directional_chart"]
    add(rows, "cross_rational_chart_exact", primary_chart["maximum_pointwise_taylor_identity_error"] < tolerance and independent_chart["maximum_identity_error"] < tolerance, [primary_chart["maximum_pointwise_taylor_identity_error"], independent_chart["maximum_identity_error"]], f"both <{tolerance}")
    add(rows, "cross_first_derivative_checks", primary_chart["maximum_first_directional_fd_relative_error"] < 1.0e-8 and independent_chart["maximum_first_fd_relative_error"] < 3.0e-7, [primary_chart["maximum_first_directional_fd_relative_error"], independent_chart["maximum_first_fd_relative_error"]], "primary <1e-8; independent <3e-7")
    add(rows, "cross_second_derivative_checks", primary_chart["maximum_second_directional_fd_relative_error"] < 3.0e-7 and independent_chart["maximum_second_fd_relative_error"] < 3.0e-7, [primary_chart["maximum_second_directional_fd_relative_error"], independent_chart["maximum_second_fd_relative_error"]], "both <3e-7")

    pdf = manifest["proof_pdf"]
    pdf_path = REPO / pdf["path"]
    add(rows, "proof_pdf_hash", digest(pdf_path) == pdf["sha256"], digest(pdf_path), pdf["sha256"])
    add(rows, "proof_pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    add(rows, "proof_pdf_size", pdf_path.stat().st_size == pdf["size_bytes"], pdf_path.stat().st_size, pdf["size_bytes"])
    add(rows, "proof_pdf_qa", pdf["pages"] > 0 and pdf["form_check"] == "PASS" and pdf["overfull_hbox_count"] == 0 and pdf["visual_qa"] == "PASS", pdf, "closed QA")

    note_text = (REPO / manifest["sources"]["proof_note"]["path"]).read_text(encoding="utf-8")
    required_tokens = (
        manifest["result_id"],
        "V_3(n)",
        "V_4(n)",
        "Sigma_j",
        "3\\alpha-1-\\kappa",
        "A7-scheme reconstruction",
        "Devil's-advocate",
        "Result footer",
    )
    add(rows, "proof_note_required_content", all(token in note_text for token in required_tokens), [token for token in required_tokens if token not in note_text], [])

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    closed = manifest["result_id"]
    next_gate = manifest["consequence"]["next_subproof"]
    closed_section = section(gates_text, f"### **{closed}**")
    add(rows, "status_stays_t4_active", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", [status.get("tier"), status.get("lifecycle")], ["T4", "ACTIVE"])
    add(rows, "status_records_closed_child_and_next", closed in status.get("statement", "") and next_gate in status.get("next_action", ""), [closed in status.get("statement", ""), next_gate in status.get("next_action", "")], [True, True])
    add(rows, "claim_records_balanced_theorem", closed in claim_text and "Sigma" in claim_text and next_gate in claim_text, [closed in claim_text, "Sigma" in claim_text, next_gate in claim_text], [True, True, True])
    add(rows, "gate_child_closed", "**Status:** CLOSED" in closed_section and "T4" in closed_section, closed_section[:300], "closed T4")
    add(rows, "roadmap_advances_to_signed_one_use", closed in roadmap_text and next_gate in roadmap_text, [closed in roadmap_text, next_gate in roadmap_text], [True, True])
    add(rows, "todo_t050_advances", "**T-050**" in todo_text and closed in todo_text and next_gate in todo_text, ["**T-050**" in todo_text, closed in todo_text, next_gate in todo_text], [True, True, True])
    add(rows, "results_register_r063", "R-063" in results_text and closed in results_text, ["R-063" in results_text, closed in results_text], [True, True])
    add(rows, "changelog_records_result", closed in changelog_text, closed in changelog_text, True)

    imported: list[str] = []
    for node in ast.walk(ast.parse(independent_script.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    add(rows, "independent_does_not_import_primary", "a13_classii_balanced_coefficient_jet_continuum" not in imported, imported, "primary absent")
    add(rows, "honesty_keeps_nelson_open", "Nelson" in manifest["honesty_boundary"] and "does not" in manifest["honesty_boundary"].lower(), manifest["honesty_boundary"], "explicit exclusion")
    add(rows, "honesty_keeps_adapted_shift_open", not manifest["claims_not_established"]["adapted_random_shift_control"], manifest["claims_not_established"], "adapted shift false")

    expected_own = int(manifest["run_contract"]["integrated_own_assertions"])
    add(rows, "integrated_own_assertion_contract", len(rows) + 2 == expected_own, len(rows) + 2, expected_own)
    child_total = int(primary["summary"]["total"]) + int(independent["summary"]["total"])
    aggregate_actual = child_total + len(rows) + 1
    expected_aggregate = int(manifest["run_contract"]["expected_total_assertions"])
    add(rows, "aggregate_assertion_count", aggregate_actual == expected_aggregate, aggregate_actual, expected_aggregate)

    own_failed = len([row for row in rows if row["status"] != "PASS"])
    child_failed = int(primary["summary"]["failed"]) + int(independent["summary"]["failed"])
    total_failed = own_failed + child_failed
    total = child_total + len(rows)
    payload = {
        "schema": "tect/a13-balanced-coefficient-jet-continuum-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": manifest_hash,
        "executed_children": not reuse,
        "primary": primary,
        "independent": independent,
        "cross_assertions": rows,
        "summary": {"passed": total - total_failed, "total": total, "failed": total_failed},
        "verdict": "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INTEGRATED-PASS" if total_failed == 0 else "FAIL",
        "consequence": manifest["consequence"],
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if total_failed:
        print(f"FAIL: integrated ({total_failed} total issue(s))")
        for row in rows:
            if row["status"] != "PASS":
                print(f" - {row['name']}: {row['actual']}")
        return 1
    print(f"PASS: integrated ({len(rows)}/{len(rows)} own; aggregate {total}/{total})")
    print("A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INTEGRATED-PASS")
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
