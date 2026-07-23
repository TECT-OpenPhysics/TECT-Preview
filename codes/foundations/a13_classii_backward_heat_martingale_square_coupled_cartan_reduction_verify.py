#!/usr/bin/env python3
"""Integrated verifier for the A13 backward-heat/Cartan reduction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = (
    CLAIM / "classii_backward_heat_martingale_square_coupled_cartan_reduction_manifest.json"
)
DEFAULT_OUTPUT = (
    CLAIM
    / "runs/2026-07-23-integrated-backward-heat-martingale-square-coupled-cartan-reduction/result.json"
)


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


def add(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    actual: Any,
    expected: Any,
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def execute(script: Path) -> None:
    completed = subprocess.run([sys.executable, str(script)], cwd=REPO, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def imported_modules(script: Path) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(ast.parse(script.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    preflight_failures = []
    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            if actual != source["sha256"]:
                preflight_failures.append((group, key, actual, source["sha256"]))
    if preflight_failures:
        print(f"FAIL: hash preflight ({len(preflight_failures)} mismatch(es)); children not executed")
        for group, key, actual, expected in preflight_failures:
            print(f" - {group}_{key}: {actual} != {expected}")
        return 1

    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    execute(primary_script)
    execute(independent_script)

    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    p = primary["computed"]
    i = independent["computed"]
    audit = manifest["integrated_audit"]
    tolerance = float(audit["identity_tolerance"])
    rows: list[dict[str, Any]] = []

    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            add(rows, f"{group}_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    expected_primary = int(manifest["run_contract"]["primary_assertions"])
    expected_independent = int(manifest["run_contract"]["independent_assertions"])
    add(rows, "verifier_version", __version__ == manifest["sources"]["verifier"]["version"], __version__, manifest["sources"]["verifier"]["version"])
    add(rows, "primary_schema", primary.get("schema") == manifest["run_contract"]["primary_schema"], primary.get("schema"), manifest["run_contract"]["primary_schema"])
    add(rows, "independent_schema", independent.get("schema") == manifest["run_contract"]["independent_schema"], independent.get("schema"), manifest["run_contract"]["independent_schema"])
    add(rows, "primary_version", primary.get("script_version") == manifest["sources"]["primary"]["version"], primary.get("script_version"), manifest["sources"]["primary"]["version"])
    add(rows, "independent_version", independent.get("script_version") == manifest["sources"]["independent"]["version"], independent.get("script_version"), manifest["sources"]["independent"]["version"])
    add(rows, "child_source_freshness", primary.get("source_sha256") == manifest["sources"]["primary"]["sha256"] and independent.get("source_sha256") == manifest["sources"]["independent"]["sha256"], [primary.get("source_sha256"), independent.get("source_sha256")], [manifest["sources"]["primary"]["sha256"], manifest["sources"]["independent"]["sha256"]])
    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(rows, "independent_pass", independent.get("pass") is True, independent.get("pass"), True)
    add(rows, "primary_assertion_contract", primary.get("assertion_count") == expected_primary, primary.get("assertion_count"), expected_primary)
    add(rows, "independent_assertion_contract", independent.get("assertion_count") == expected_independent, independent.get("assertion_count"), expected_independent)
    add(rows, "primary_assertion_flags", len(primary.get("assertions", {})) == expected_primary and all(value is True for value in primary.get("assertions", {}).values()), {"length": len(primary.get("assertions", {})), "false": [key for key, value in primary.get("assertions", {}).items() if value is not True]}, {"length": expected_primary, "false": []})
    add(rows, "independent_assertion_flags", len(independent.get("assertions", {})) == expected_independent and all(value is True for value in independent.get("assertions", {}).values()), {"length": len(independent.get("assertions", {})), "false": [key for key, value in independent.get("assertions", {}).items() if value is not True]}, {"length": expected_independent, "false": []})
    result_id = manifest["result_id"]
    add(rows, "shared_result_id", primary.get("result_id") == independent.get("result_id") == result_id, [primary.get("result_id"), independent.get("result_id")], result_id)
    strict_past = json.loads((REPO / manifest["authority"]["a13_strict_past_manifest"]["path"]).read_text(encoding="utf-8"))
    expected_q = 1.0 / (2.0 * float(strict_past["audit"]["epsilon_control"]))
    add(rows, "q_derived_from_pinned_authority", abs(float(primary["inputs"]["q"]) - expected_q) < tolerance and abs(float(independent["inputs"]["q"]) - expected_q) < tolerance, [primary["inputs"]["q"], independent["inputs"]["q"]], expected_q)
    strict_past_hash = manifest["authority"]["a13_strict_past_manifest"]["sha256"]
    add(rows, "child_q_authority_freshness", primary["inputs"].get("q_authority_sha256") == strict_past_hash and independent["inputs"].get("q_authority_sha256") == strict_past_hash, [primary["inputs"].get("q_authority_sha256"), independent["inputs"].get("q_authority_sha256")], strict_past_hash)

    identity_values = {
        "primary_conditional_martingale": p["conditional_martingale_residual"],
        "primary_controlled_telescope": p["controlled_telescope_residual"],
        "independent_controlled_telescope": i["independent_telescope_residual"],
        "primary_completion": p["completion_residual"],
        "independent_completion": i["independent_completion_residual"],
        "primary_gibbs_pythagoras": p["gibbs_pythagoras_residual"],
        "independent_gibbs_pythagoras": i["independent_gibbs_pythagoras_residual"],
        "primary_partition_formula": p["partition_formula_residual"],
        "independent_partition_formula": i["independent_partition_formula_residual"],
        "primary_quartic_identity": p["quartic_identity_residual"],
        "independent_quartic_identity": i["independent_quartic_residual"],
        "primary_frame_secant": p["averaged_frame_secant_residual"],
        "independent_frame_secant": i["independent_frame_secant_residual"],
    }
    add(rows, "all_exact_residuals_close", max(float(v) for v in identity_values.values()) < tolerance, identity_values, f"maximum<{tolerance}")
    add(rows, "triangular_entropy_chain", float(i["triangular_entropy_chain_residual"]) < tolerance, i["triangular_entropy_chain_residual"], f"<{tolerance}")
    pullback_minimum = float(audit["pullback_negative_control_minimum"])
    add(rows, "state_past_pullback_negative_control", float(i["raw_past_without_pullback_failure"]) > pullback_minimum, i["raw_past_without_pullback_failure"], f">{pullback_minimum}")

    growth_bound = math.sqrt(float(audit["frame_growth_squared_bound"]))
    lipschitz_bound = math.sqrt(float(audit["frame_lipschitz_squared_bound"]))
    frame_values = [
        float(p["maximum_frame_growth_ratio"]),
        float(i["independent_frame_growth_maximum"]),
    ]
    lipschitz_values = [
        float(p["maximum_frame_lipschitz_ratio"]),
        float(i["independent_frame_lipschitz_maximum"]),
    ]
    add(rows, "frame_growth_bound", max(frame_values) <= growth_bound, frame_values, f"<={growth_bound}")
    add(rows, "frame_lipschitz_bound", max(lipschitz_values) <= lipschitz_bound, lipschitz_values, f"<={lipschitz_bound}")
    add(rows, "factor_four_and_positive_remainder", float(p["factor_four_residual"]) < tolerance and min(float(p["minimum_quartic_remainder"]), float(i["independent_quartic_minimum_remainder"])) >= -tolerance, [p["factor_four_residual"], p["minimum_quartic_remainder"], i["independent_quartic_minimum_remainder"]], "identity close and remainder nonnegative")
    terminal_minimum = float(audit["terminal_only_failure_minimum"])
    add(rows, "terminal_only_negative_control", float(p["terminal_only_failure_witness"]) > terminal_minimum, p["terminal_only_failure_witness"], f">{terminal_minimum}")

    expected_covariance_ratio = 1.0 / float(audit["covariance_square_ratio_denominator"])
    expected_mixed_ratio = 1.0 / float(audit["mixed_trace_ratio_denominator"])
    add(rows, "dyadic_trace_gains", abs(float(p["covariance_square_dyadic_ratio"]) - expected_covariance_ratio) < tolerance and abs(float(p["mixed_trace_dyadic_ratio"]) - expected_mixed_ratio) < tolerance, [p["covariance_square_dyadic_ratio"], p["mixed_trace_dyadic_ratio"]], [expected_covariance_ratio, expected_mixed_ratio])
    add(rows, "scalar_heat_plateau", max(float(p["heat_plateau_max_deviation"]), float(i["independent_heat_plateau_deviation"])) < tolerance, [p["heat_plateau_max_deviation"], i["independent_heat_plateau_deviation"]], f"maximum<{tolerance}")
    heat_factor = float(audit["heat_to_shell_sixth_minimum_factor"])
    add(rows, "shellwise_heat_beats_sextic", float(i["independent_heat_absolute_sum"]) > heat_factor * float(i["independent_shell_sixth_sum"]), [i["independent_heat_absolute_sum"], i["independent_shell_sixth_sum"]], f"ratio>{heat_factor}")

    deficits = p["production_origin_deficits"]
    deficit_minimum = float(audit["production_deficit_minimum"])
    deficit_maximum = float(audit["production_deficit_maximum"])
    deficit_values = [float(deficits[key]) for key in sorted(deficits)]
    add(rows, "production_deficit_interval", all(deficit_minimum < value < deficit_maximum for value in deficit_values), deficits, f"each in ({deficit_minimum},{deficit_maximum})")
    plateau_maximum = float(audit["production_relative_plateau_maximum"])
    add(rows, "production_plateau_stability", float(p["production_origin_relative_plateau_gap"]) < plateau_maximum, p["production_origin_relative_plateau_gap"], f"<{plateau_maximum}")
    quadrature_maximum = float(audit["production_quadrature_relative_gap_maximum"])
    quadrature_gaps = {key: float(value) for key, value in p["production_origin_quadrature_relative_gaps"].items()}
    add(rows, "production_quadrature_stability", max(quadrature_gaps.values()) < quadrature_maximum, quadrature_gaps, f"maximum<{quadrature_maximum}")
    zero_floor_value = float(i["zero_floor_isotropic_deficit_coefficient"])
    zero_floor_oracle = float(audit["zero_floor_isotropic_deficit_test_oracle"])
    zero_floor_tolerance = float(audit["zero_floor_isotropic_deficit_tolerance"])
    add(rows, "zero_floor_isotropic_diagnostic", independent["inputs"].get("isotropic_diagnostic_floor", "").startswith("e=0") and abs(zero_floor_value - zero_floor_oracle) < zero_floor_tolerance, {"value": zero_floor_value, "floor": independent["inputs"].get("isotropic_diagnostic_floor")}, {"value": f"{zero_floor_oracle}+/-{zero_floor_tolerance}", "floor": "e=0"})

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_text = note_path.read_text(encoding="utf-8")
    note_tokens = tuple(manifest["integrated_audit"]["proof_note_required_tokens"])
    add(rows, "proof_note_required_content", all(token in note_text for token in note_tokens), [token for token in note_tokens if token not in note_text], [])
    add(rows, "proof_note_notation_collision_removed", "K_j={1\\over q}\\log" not in note_text and "\\kappa_j={1\\over q}\\log" in note_text, "K_j log normalizer absent" if "K_j={1\\over q}\\log" not in note_text else "collision present", "kappa_j normalizer")
    add(rows, "proof_note_floor_boundary", "analytic zero-floor diagnostic" in note_text and "positive-floor lower-bound" in note_text, ["analytic zero-floor diagnostic" in note_text, "positive-floor lower-bound" in note_text], [True, True])

    pdf = manifest["proof_pdf"]
    pdf_path = REPO / pdf["path"]
    pdf_hash = digest(pdf_path)
    pdf_pages = len(PdfReader(str(pdf_path)).pages)
    add(rows, "proof_pdf_hash", pdf_hash == pdf["sha256"], pdf_hash, pdf["sha256"])
    add(rows, "proof_pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    add(rows, "proof_pdf_size", pdf_path.stat().st_size == pdf["size_bytes"], pdf_path.stat().st_size, pdf["size_bytes"])
    add(rows, "proof_pdf_pages", pdf_pages == pdf["pages"], pdf_pages, pdf["pages"])
    add(rows, "proof_pdf_qa", pdf["form_check"] == "PASS" and pdf["overfull_hbox_count"] == 0 and pdf["visual_qa"] == "PASS", pdf, "form PASS, zero overfull, visual PASS")

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negative_text = (REPO / "negative-results" / "registry.md").read_text(encoding="utf-8")
    next_gate = manifest["consequence"]["next_subgate"]
    umbrella = manifest["consequence"]["umbrella_gate"]
    negative_id = manifest["consequence"]["negative_result"]
    add(rows, "status_t4_and_umbrella_open", status.get("tier") == "T4" and status.get("open_gates") == [umbrella], [status.get("tier"), status.get("open_gates")], ["T4", [umbrella]])
    add(rows, "status_records_reduction_and_next", result_id in status.get("statement", "") and next_gate in status.get("next_action", ""), [result_id in status.get("statement", ""), next_gate in status.get("next_action", "")], [True, True])
    add(rows, "claim_records_honesty_boundary", result_id in claim_text and next_gate in claim_text and "one-shot" in claim_text.lower(), [result_id in claim_text, next_gate in claim_text, "one-shot" in claim_text.lower()], [True, True, True])
    add(rows, "gates_record_scoped_advance", result_id in gates_text and next_gate in gates_text and "REDUCED-NOT-CLOSED" in gates_text, [result_id in gates_text, next_gate in gates_text, "REDUCED-NOT-CLOSED" in gates_text], [True, True, True])
    add(rows, "roadmap_records_reduction", result_id in roadmap_text and next_gate in roadmap_text, [result_id in roadmap_text, next_gate in roadmap_text], [True, True])
    add(rows, "todo_keeps_t050_in_progress", "**T-050**" in todo_text and result_id in todo_text and next_gate in todo_text, ["**T-050**" in todo_text, result_id in todo_text, next_gate in todo_text], [True, True, True])
    add(rows, "changelog_records_package", result_id in changelog_text, result_id in changelog_text, True)
    ledger_id = manifest["consequence"]["result_ledger_id"]
    add(rows, "results_ledger_records_result", ledger_id in results_text and result_id in results_text, [ledger_id in results_text, result_id in results_text], [True, True])
    add(rows, "negative_registry_records_no_go", negative_id in negative_text, negative_id in negative_text, True)
    add(rows, "manifest_preserves_open_boundary", all(value is False for value in manifest["claims_not_established"].values()), manifest["claims_not_established"], "all false")

    modules = imported_modules(independent_script)
    primary_module = primary_script.stem
    add(rows, "independent_does_not_import_primary", primary_module not in modules, modules, f"{primary_module} absent")
    forbidden_local_helpers = tuple(manifest["independent_audit"]["forbidden_local_imports"])
    imported_forbidden = [module for module in modules if module in forbidden_local_helpers]
    add(rows, "independent_reconstructs_production_helpers", not imported_forbidden, imported_forbidden, [])

    environment = manifest["environment_contract"]
    requirements_text = (REPO / environment["requirements_path"]).read_text(encoding="utf-8")
    build_text = (REPO / environment["build_tool_path"]).read_text(encoding="utf-8")
    doctor_text = (REPO / environment["doctor_path"]).read_text(encoding="utf-8")
    note_check_text = (REPO / environment["note_pdf_check_path"]).read_text(encoding="utf-8")
    add(rows, "pdf_environment_contract", all(package in requirements_text for package in environment["python_packages"]) and "tectonic" in build_text.lower() and "pdf-python-runtime" in doctor_text and "tex-engine" in doctor_text and "tex_engine" in note_check_text, {"packages": [package in requirements_text for package in environment["python_packages"]], "build_tectonic": "tectonic" in build_text.lower(), "doctor_pdf": "pdf-python-runtime" in doctor_text, "doctor_tex": "tex-engine" in doctor_text, "strict_tex": "tex_engine" in note_check_text}, "all true")

    child_total = int(primary["assertion_count"]) + int(independent["assertion_count"])
    expected_integrated = int(manifest["run_contract"]["integrated_assertions"])
    add(rows, "integrated_assertion_contract", len(rows) + 2 == expected_integrated, len(rows) + 2, expected_integrated)
    expected_aggregate = int(manifest["run_contract"]["aggregate_assertions"])
    add(rows, "aggregate_assertion_contract", child_total + len(rows) + 1 == expected_aggregate, child_total + len(rows) + 1, expected_aggregate)
    failures = [row for row in rows if row["status"] != "PASS"]
    child_failed = 0 if primary.get("pass") and independent.get("pass") else child_total
    total = child_total + len(rows)
    failed = child_failed + len(failures)
    payload = {
        "schema": manifest["run_contract"]["integrated_schema"],
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
        "verdict": f"{result_id}-INTEGRATED-PASS" if not failures and failed == 0 else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures or failed:
        print(f"FAIL: integrated ({failed} total failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {total}/{total}")
    print(f"{result_id}-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
