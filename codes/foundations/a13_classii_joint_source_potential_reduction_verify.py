#!/usr/bin/env python3
"""One-command verifier for the A13 joint source-potential reduction."""

from __future__ import annotations

import argparse
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

__version__ = "1.0.1"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_joint_source_potential_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-integrated-joint-source-potential-reduction-v1.1" / "result.json"


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


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def execute(script: Path, manifest: Path, output: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(script), "--manifest", str(manifest), "--output", str(output)],
        cwd=REPO,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run(manifest_path: Path, output_path: Path, reuse: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
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

    primary_summary = primary.get("summary", {})
    independent_summary = independent.get("summary", {})
    current_manifest_hash = digest(manifest_path)
    add(rows, "primary_manifest_and_assertion_count", primary.get("manifest_sha256") == current_manifest_hash and primary_summary.get("total") == manifest["run_contract"]["primary_assertions"], [primary.get("manifest_sha256"), primary_summary], [current_manifest_hash, manifest["run_contract"]["primary_assertions"]])
    add(rows, "independent_manifest_and_assertion_count", independent.get("manifest_sha256") == current_manifest_hash and independent_summary.get("total") == manifest["run_contract"]["independent_assertions"], [independent.get("manifest_sha256"), independent_summary], [current_manifest_hash, manifest["run_contract"]["independent_assertions"]])
    add(rows, "primary_all_pass", primary_summary.get("failed") == 0, primary_summary, "failed=0")
    add(rows, "independent_all_pass", independent_summary.get("failed") == 0, independent_summary, "failed=0")

    p_derived = primary["derived"]
    i_derived = independent["derived"]
    tolerance = float(manifest["integrated_audit"]["cross_tolerance"])
    certificate_tolerance = float(manifest["integrated_audit"]["certificate_tolerance"])
    add(rows, "cross_beta_operator", abs(float(p_derived["coefficients"]["beta_operator"]) - float(i_derived["beta_operator"])) < tolerance, [p_derived["coefficients"]["beta_operator"], i_derived["beta_operator"]], f"difference<{tolerance}")
    add(rows, "cross_symbol_coercivity", abs(float(p_derived["symbol_coercivity"]) - float(i_derived["symbol_coercivity"])) < tolerance, [p_derived["symbol_coercivity"], i_derived["symbol_coercivity"]], f"difference<{tolerance}")
    for key in ("full_l2_second", "past_l4_fourth", "full_l6_sixth", "past_l6_sixth", "nonpositive_cubic_energy", "mixed_hardy_functional"):
        p_value = float(p_derived["certificate"][key])
        i_value = float(i_derived["certificate"][key])
        add(rows, f"cross_certificate_{key}", abs(p_value - i_value) < certificate_tolerance, [p_value, i_value], f"difference<{certificate_tolerance}")
    for key in ("past_amplification", "terminal_joint_ratio", "past_joint_exponent_reward"):
        p_value = float(p_derived["source"][key])
        i_value = float(i_derived["source"][key])
        add(rows, f"cross_source_{key}", abs(p_value - i_value) < certificate_tolerance, [p_value, i_value], f"difference<{certificate_tolerance}")
    add(rows, "both_factor_two_fixtures_pass", p_derived["joint_source_doubling"]["retained_samples"] >= manifest["audit"]["minimum_retained_samples"] and i_derived["joint_source_doubling"]["retained_samples"] >= manifest["independent_audit"]["minimum_retained_samples"] and p_derived["joint_source_doubling"]["max_total_vs_two_frozen_relative_error"] < manifest["audit"]["doubling_tolerance"] and i_derived["joint_source_doubling"]["max_total_vs_two_frozen_relative_error"] < manifest["independent_audit"]["doubling_tolerance"], [p_derived["joint_source_doubling"], i_derived["joint_source_doubling"]], "both fixtures nonvacuous and errors below tolerance")
    add(rows, "both_gaussian_identities_pass", p_derived["gaussian_identity"]["max_pointwise_log_density_error"] < manifest["audit"]["gaussian_tolerance"] and i_derived["gaussian_identity"]["absolute_error"] < manifest["independent_audit"]["hermite_tolerance"], [p_derived["gaussian_identity"], i_derived["gaussian_identity"]], "both exact/completed checks pass")
    add(rows, "cross_frozen_mixed_threshold", abs(float(p_derived["mixed_hardy"]["frozen_tensor_threshold"]) - float(i_derived["mixed_hardy"]["frozen_tensor_threshold"])) < tolerance, [p_derived["mixed_hardy"]["frozen_tensor_threshold"], i_derived["mixed_hardy"]["frozen_tensor_threshold"]], f"difference<{tolerance}")
    add(rows, "cross_joint_mixed_threshold", abs(float(p_derived["mixed_hardy"]["joint_factor_four_tensor_threshold"]) - float(i_derived["mixed_hardy"]["joint_factor_four_tensor_threshold"])) < tolerance, [p_derived["mixed_hardy"]["joint_factor_four_tensor_threshold"], i_derived["mixed_hardy"]["joint_factor_four_tensor_threshold"]], f"difference<{tolerance}")
    add(rows, "cross_factor_four_cm_cost", abs(float(p_derived["cm_sextic"]["registered_factor_four_source_sextic_cost"]) - float(i_derived["cm_sextic"]["registered_factor_four_source_sextic_cost"])) < tolerance, [p_derived["cm_sextic"]["registered_factor_four_source_sextic_cost"], i_derived["cm_sextic"]["registered_factor_four_source_sextic_cost"]], f"difference<{tolerance}")
    add(rows, "cross_factor_four_frozen_theta", abs(float(p_derived["cm_sextic"]["factor_four_frozen_theta"]) - float(i_derived["cm_sextic"]["factor_four_frozen_theta"])) < tolerance, [p_derived["cm_sextic"]["factor_four_frozen_theta"], i_derived["cm_sextic"]["factor_four_frozen_theta"]], f"difference<{tolerance}")
    add(rows, "cross_factor_four_unexponentiated_cost", abs(float(p_derived["cm_sextic"]["registered_factor_four_unexponentiated_source_sextic_cost"]) - float(i_derived["cm_sextic"]["registered_factor_four_unexponentiated_source_sextic_cost"])) < tolerance, [p_derived["cm_sextic"]["registered_factor_four_unexponentiated_source_sextic_cost"], i_derived["cm_sextic"]["registered_factor_four_unexponentiated_source_sextic_cost"]], f"difference<{tolerance}")
    add(rows, "cross_frozen_reference_p_upper", abs(float(p_derived["cm_sextic"]["frozen_source_reference_p_upper_at_registered_theta"]) - float(i_derived["cm_sextic"]["frozen_source_reference_p_upper_at_registered_theta"])) < tolerance, [p_derived["cm_sextic"]["frozen_source_reference_p_upper_at_registered_theta"], i_derived["cm_sextic"]["frozen_source_reference_p_upper_at_registered_theta"]], f"difference<{tolerance}")
    add(rows, "cross_equivalent_nelson_exponent", abs(float(p_derived["one_use_equivalence"]["equivalent_nelson_exponent_q"]) - float(i_derived["one_use_equivalence"]["equivalent_nelson_exponent_q"])) < tolerance, [p_derived["one_use_equivalence"]["equivalent_nelson_exponent_q"], i_derived["one_use_equivalence"]["equivalent_nelson_exponent_q"]], f"difference<{tolerance}")
    add(rows, "cross_one_use_margins", abs(float(p_derived["one_use_equivalence"]["sextic_margin"]) - float(i_derived["one_use_equivalence"]["sextic_margin"])) < tolerance and abs(float(p_derived["one_use_equivalence"]["control_margin"]) - float(i_derived["one_use_equivalence"]["control_margin"])) < tolerance, [p_derived["one_use_equivalence"], i_derived["one_use_equivalence"]], f"both differences<{tolerance}")
    add(rows, "cross_scalar_doob_leading_coefficient", abs(float(p_derived["scalar_doob_loop"]["leading_A6_coefficient"]) - float(i_derived["scalar_doob_loop"]["leading_A6_coefficient"])) < tolerance, [p_derived["scalar_doob_loop"]["leading_A6_coefficient"], i_derived["scalar_doob_loop"]["leading_A6_coefficient"]], f"difference<{tolerance}")
    add(rows, "cross_ramer_unit_negative_eigenvalue", abs(float(p_derived["nonfrozen_ramer"]["unit_minimum_real_eigenvalue"]) - float(i_derived["nonfrozen_ramer"]["unit_minimum_real_eigenvalue"])) < certificate_tolerance, [p_derived["nonfrozen_ramer"]["unit_minimum_real_eigenvalue"], i_derived["nonfrozen_ramer"]["unit_minimum_real_eigenvalue"]], f"difference<{certificate_tolerance}")
    add(rows, "cross_ramer_singularity_scale", abs(float(p_derived["nonfrozen_ramer"]["root_estimate"]) - float(i_derived["nonfrozen_ramer"]["root_estimate"])) < certificate_tolerance, [p_derived["nonfrozen_ramer"]["root_estimate"], i_derived["nonfrozen_ramer"]["root_estimate"]], f"difference<{certificate_tolerance}")
    add(rows, "cross_ramer_curl_coefficient", abs(float(p_derived["nonfrozen_ramer"]["analytic_curl_coefficient_at_u1"]) - float(i_derived["nonfrozen_ramer"]["analytic_curl_coefficient_at_u1"])) < tolerance, [p_derived["nonfrozen_ramer"]["analytic_curl_coefficient_at_u1"], i_derived["nonfrozen_ramer"]["analytic_curl_coefficient_at_u1"]], f"difference<{tolerance}")
    add(rows, "cross_direct_ramer_square_charge", abs(float(p_derived["direct_ramer_square_carrier_charge"]) - float(i_derived["direct_ramer_square_carrier_charge"])) < certificate_tolerance, [p_derived["direct_ramer_square_carrier_charge"], i_derived["direct_ramer_square_carrier_charge"]], f"difference<{certificate_tolerance}")
    add(rows, "cross_schatten_boundary_fixture", abs(float(p_derived["schatten_boundary"]["hs_log_partition_uniform_bound"]) - float(i_derived["schatten_boundary"]["hs_log_partition_uniform_bound"])) < tolerance and abs(float(p_derived["schatten_boundary"]["non_hs_point_exponent_growth"]) - float(i_derived["schatten_boundary"]["non_hs_point_exponent_growth"])) < tolerance, [p_derived["schatten_boundary"]["hs_log_partition_uniform_bound"], i_derived["schatten_boundary"]["hs_log_partition_uniform_bound"], p_derived["schatten_boundary"]["non_hs_point_exponent_growth"], i_derived["schatten_boundary"]["non_hs_point_exponent_growth"]], f"both differences<{tolerance}")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_text = note_path.read_text(encoding="utf-8")
    required_note_tokens = (
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
        "NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER",
        "ell_{\\rm joint}=2\\ell_{\\rm frozen}",
        "{64\\over9}",
        "alternative diagnostics",
        "0.0445558902",
        "1/(2\\epsilon_v)",
        "NG-2026-07-22-A13-TIMEWISE-YOUNG-CARRE-DU-CHAMP",
        "NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT",
        "5/9",
        "does not prove the A7 Nelson bound",
    )
    add(rows, "proof_note_required_content", all(token in note_text for token in required_note_tokens), [token for token in required_note_tokens if token not in note_text], [])
    pdf_spec = manifest["proof_pdf"]
    pdf_path = REPO / pdf_spec["path"]
    actual_pdf_hash = digest(pdf_path)
    add(rows, "proof_pdf_hash", actual_pdf_hash == pdf_spec["sha256"], actual_pdf_hash, pdf_spec["sha256"])
    add(rows, "proof_pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    add(rows, "proof_pdf_size", pdf_path.stat().st_size == pdf_spec["size_bytes"], pdf_path.stat().st_size, pdf_spec["size_bytes"])

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    registry_text = (REPO / "negative-results" / "registry.md").read_text(encoding="utf-8")
    next_gate = manifest["consequence"]["next_gate"]
    add(rows, "status_tier_stays_t4", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", [status.get("tier"), status.get("lifecycle")], ["T4", "ACTIVE"])
    add(rows, "status_has_exact_successor", status.get("open_gates") == [next_gate], status.get("open_gates"), [next_gate])
    add(rows, "status_no_overclaim", "does not prove" in status.get("no_overclaim", "").lower() and "T5" in status.get("no_overclaim", ""), status.get("no_overclaim"), "explicit Nelson and T5 exclusions")
    add(rows, "claim_records_reduced_not_closed", "REDUCED-NOT-CLOSED" in claim_text and next_gate in claim_text, ["REDUCED-NOT-CLOSED" in claim_text, next_gate in claim_text], [True, True])
    add(rows, "gates_records_local_nogo_and_successor", "LOCAL-BELLMAN-BARRIER" in gates_text and next_gate in gates_text, ["LOCAL-BELLMAN-BARRIER" in gates_text, next_gate in gates_text], [True, True])
    add(rows, "roadmap_records_successor", next_gate in roadmap_text and "factor four" in roadmap_text.lower(), [next_gate in roadmap_text, "factor four" in roadmap_text.lower()], [True, True])
    add(rows, "todo_keeps_t050_in_progress", "**T-050**" in todo_text and next_gate in todo_text and "In progress" in todo_text, ["**T-050**" in todo_text, next_gate in todo_text], [True, True])
    add(rows, "negative_registry_has_local_bellman_nogo", "NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER" in registry_text, "registry token", "present")
    add(rows, "negative_registry_has_timewise_young_nogo", "NG-2026-07-22-A13-TIMEWISE-YOUNG-CARRE-DU-CHAMP" in registry_text, "registry token", "present")
    add(rows, "negative_registry_has_factor_four_audit", "AUDIT-2026-07-22-A13-FACTOR-FOUR-ALLOCATION" in registry_text, "registry token", "present")
    add(rows, "negative_registry_has_nonfrozen_ramer_nogo", "NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT" in registry_text, "registry token", "present")
    independent_text = independent_script.read_text(encoding="utf-8")
    add(rows, "independent_does_not_import_primary", "a13_classii_joint_source_potential_reduction import" not in independent_text, "primary import" in independent_text, False)
    expected_integrated_own = int(manifest["run_contract"]["integrated_own_assertions"])
    add(rows, "integrated_own_assertion_contract", len(rows) + 2 == expected_integrated_own, len(rows) + 2, expected_integrated_own)

    failures = [row for row in rows if row["status"] != "PASS"]
    total_before_aggregate = int(primary_summary.get("total", 0)) + int(independent_summary.get("total", 0)) + len(rows)
    expected_total = int(manifest["run_contract"]["expected_total_assertions"])
    aggregate_ok = total_before_aggregate + 1 == expected_total
    aggregate = {"name": "aggregate_assertion_count", "status": "PASS" if aggregate_ok else "FAIL", "actual": total_before_aggregate + 1, "expected": expected_total}
    rows.append(aggregate)
    if not aggregate_ok:
        failures.append(aggregate)
    total = total_before_aggregate + 1
    own_failed = len([row for row in rows if row["status"] != "PASS"])
    child_failed = int(primary_summary.get("failed", 0)) + int(independent_summary.get("failed", 0))
    total_failed = child_failed + own_failed
    passed = int(primary_summary.get("passed", 0)) + int(independent_summary.get("passed", 0)) + len(rows) - own_failed
    payload = {
        "schema": "tect/a13-classii-joint-source-potential-reduction-integrated-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "primary": primary,
        "independent": independent,
        "cross_assertions": rows,
        "summary": {"passed": passed, "total": total, "failed": total_failed},
        "verdict": "A13-CLASSII-JOINT-SOURCE-POTENTIAL-REDUCTION-INTEGRATED-PASS" if not failures else "FAIL",
        "consequence": manifest["consequence"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: integrated ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {passed}/{total}")
    print("A13-CLASSII-JOINT-SOURCE-POTENTIAL-REDUCTION-INTEGRATED-PASS")
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
