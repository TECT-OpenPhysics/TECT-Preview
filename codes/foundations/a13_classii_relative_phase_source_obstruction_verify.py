#!/usr/bin/env python3
"""One-command verifier for the A13 relative-phase source obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.1"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_relative_phase_source_obstruction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-21-integrated-relative-phase-obstruction" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def execute(script: Path, manifest: Path, output: Path) -> None:
    command = [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)]
    completed = subprocess.run(command, cwd=REPO, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run(manifest_path: Path, output_path: Path, reuse: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    primary_path = REPO / manifest["run_contract"]["primary_output"]
    independent_path = REPO / manifest["run_contract"]["independent_output"]
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]

    if not reuse or not primary_path.exists():
        execute(primary_script, manifest_path, primary_path)
    if not reuse or not independent_path.exists():
        execute(independent_script, manifest_path, independent_path)

    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    independent = json.loads(independent_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, source in manifest["sources"].items():
        actual = digest(REPO / source["path"])
        add(rows, f"integrated_source_{key}_hash", actual == source["sha256"], actual, source["sha256"])
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"integrated_authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    p_summary = primary.get("summary", {})
    i_summary = independent.get("summary", {})
    add(rows, "primary_assertion_count", p_summary.get("total") == manifest["run_contract"]["primary_assertions"], p_summary, manifest["run_contract"]["primary_assertions"])
    add(rows, "independent_assertion_count", i_summary.get("total") == manifest["run_contract"]["independent_assertions"], i_summary, manifest["run_contract"]["independent_assertions"])
    add(rows, "primary_all_pass", p_summary.get("failed") == 0, p_summary, "failed=0")
    add(rows, "independent_all_pass", i_summary.get("failed") == 0, i_summary, "failed=0")

    p_derived = primary["derived"]
    i_derived = independent["derived"]
    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    p_certificate = p_derived["certificate"]
    i_certificate = i_derived["certificate"]
    add(rows, "cross_beta_operator", abs(float(p_derived["coefficients"]["beta_operator"]) - float(i_derived["beta_operator"])) < tolerance, [p_derived["coefficients"]["beta_operator"], i_derived["beta_operator"]], f"difference<{tolerance}")
    add(rows, "cross_full_l6", abs(float(p_certificate["full_l6_sixth"]) - float(i_certificate["full_l6_sixth"])) < float(manifest["integrated_audit"]["certificate_tolerance"]), [p_certificate["full_l6_sixth"], i_certificate["full_l6_sixth"]], "routes agree")
    add(rows, "cross_past_l6", abs(float(p_certificate["past_l6_sixth"]) - float(i_certificate["past_l6_sixth"])) < float(manifest["integrated_audit"]["certificate_tolerance"]), [p_certificate["past_l6_sixth"], i_certificate["past_l6_sixth"]], "routes agree")
    add(rows, "cross_nonpositive_energy", abs(float(p_certificate["nonpositive_cubic_energy"]) - float(i_certificate["nonpositive_cubic_energy"])) < float(manifest["integrated_audit"]["certificate_tolerance"]), [p_certificate["nonpositive_cubic_energy"], i_certificate["nonpositive_cubic_energy"]], "routes agree")
    add(rows, "cross_spin_functional", abs(float(p_certificate["spin_functional"]) - float(i_certificate["spin_functional"])) < float(manifest["integrated_audit"]["spin_tolerance"]), [p_certificate["spin_functional"], i_certificate["spin_functional"]], "routes agree")
    add(rows, "cross_source_ratio", abs(float(p_certificate["source_ratio"]) - float(i_certificate["source_ratio"])) < float(manifest["integrated_audit"]["source_tolerance"]), [p_certificate["source_ratio"], i_certificate["source_ratio"]], "routes agree")

    gamma_third = float(p_derived["budget"]["gamma_over_three"])
    source_minimum = min(float(p_certificate["source_ratio"]), float(i_certificate["source_ratio"]))
    add(rows, "both_routes_exceed_gamma_third", source_minimum > gamma_third, source_minimum, gamma_third)
    add(rows, "both_routes_have_declared_margin", source_minimum - gamma_third > float(manifest["certificate"]["required_margin_over_gamma_third"]), source_minimum - gamma_third, f">{manifest['certificate']['required_margin_over_gamma_third']}")

    note_text = (REPO / manifest["sources"]["proof_note"]["path"]).read_text(encoding="utf-8")
    proof_pdf_spec = manifest["proof_pdf"]
    proof_pdf_path = REPO / proof_pdf_spec["path"]
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    required_tokens = (
        "B(X)\\mathcal JZ=0",
        "A13-CLASSII-JOINT-SOURCE-POTENTIAL-LOG-LAPLACE",
        "NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET",
        "does not rule out",
    )
    add(rows, "proof_note_required_boundaries", all(token in note_text for token in required_tokens), [token for token in required_tokens if token not in note_text], [])
    proof_pdf_hash = digest(proof_pdf_path)
    add(rows, "proof_pdf_hash", proof_pdf_hash == proof_pdf_spec["sha256"], proof_pdf_hash, proof_pdf_spec["sha256"])
    pdf_signature = proof_pdf_path.read_bytes()[:5]
    add(rows, "proof_pdf_signature", pdf_signature == b"%PDF-", pdf_signature.decode("ascii", errors="replace"), "%PDF-")
    claim_lower = re.sub(r"\s+", " ", claim_text.lower())
    claim_negative_marker = any(marker in claim_lower for marker in ("closed negatively", "closed-negative", "closed negative"))
    add(rows, "claim_records_negative_t049", "T-049" in claim_text and claim_negative_marker, {"t049": "T-049" in claim_text, "negative_marker": claim_negative_marker}, True)
    add(rows, "status_tier_t4", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", [status.get("tier"), status.get("lifecycle")], ["T4", "ACTIVE"])
    add(rows, "status_no_t5_overclaim", "T5" in status.get("no_overclaim", "") and "does not" in status.get("no_overclaim", "").lower(), status.get("no_overclaim"), "explicit T5 exclusion")
    add(rows, "current_open_gates_match_status", status.get("open_gates") == manifest["consequence"]["current_open_gates"], status.get("open_gates"), manifest["consequence"]["current_open_gates"])

    independent_source = independent_script.read_text(encoding="utf-8")
    add(rows, "independent_does_not_import_primary", "a13_classii_relative_phase_source_obstruction import" not in independent_source, "primary import" in independent_source, False)
    add(rows, "negative_registry_entry_present", "NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET" in (REPO / "negative-results" / "registry.md").read_text(encoding="utf-8"), "registry token", "present")

    failures = [row for row in rows if row["status"] != "PASS"]
    total_assertions = int(p_summary.get("total", 0)) + int(i_summary.get("total", 0)) + len(rows)
    passed_assertions = int(p_summary.get("passed", 0)) + int(i_summary.get("passed", 0)) + len(rows) - len(failures)
    add_expected = int(manifest["run_contract"]["expected_total_assertions"])
    aggregate_ok = total_assertions + 1 == add_expected
    aggregate_row = {"name": "aggregate_assertion_count", "status": "PASS" if aggregate_ok else "FAIL", "actual": total_assertions + 1, "expected": add_expected}
    rows.append(aggregate_row)
    if not aggregate_ok:
        failures.append(aggregate_row)
    total_assertions += 1
    passed_assertions += 1 if aggregate_ok else 0

    result = {
        "schema": "tect/a13-classii-relative-phase-source-obstruction-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "primary": primary,
        "independent": independent,
        "cross_assertions": rows,
        "summary": {"passed": passed_assertions, "total": total_assertions, "failed": len(failures)},
        "verdict": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION-INTEGRATED-PASS" if not failures else "FAIL",
        "consequence": manifest["consequence"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"FAIL: integrated ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {passed_assertions}/{total_assertions}")
    print("A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION-INTEGRATED-PASS")
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
