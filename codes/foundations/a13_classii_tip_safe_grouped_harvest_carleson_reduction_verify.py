#!/usr/bin/env python3
"""Integrated verifier for the A13 tip-safe grouped-harvest reduction."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_tip_safe_grouped_harvest_carleson_reduction_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs/2026-07-23-integrated-tip-safe-grouped-harvest-carleson-reduction/result.json"
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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
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


def text_contains(path: Path, tokens: list[str]) -> tuple[bool, list[str]]:
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in tokens if token not in content]
    return not missing, missing


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    preflight = []
    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            if actual != source["sha256"]:
                preflight.append((group, key, actual, source["sha256"]))
    pdf_source = manifest["proof_pdf"]
    pdf_actual = digest(REPO / pdf_source["path"])
    if pdf_actual != pdf_source["sha256"]:
        preflight.append(("proof_pdf", "pdf", pdf_actual, pdf_source["sha256"]))
    if preflight:
        print(f"FAIL: hash preflight ({len(preflight)} mismatch(es)); children not executed")
        for group, key, actual, expected in preflight:
            print(f" - {group}_{key}: {actual} != {expected}")
        return 1

    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    execute(primary_script)
    execute(independent_script)
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    p = primary["computed"]
    i = independent["computed"]
    rows: list[dict[str, Any]] = []

    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            add(rows, f"{group}_{key}_hash", actual == source["sha256"], actual, source["sha256"])
    add(rows, "proof_pdf_hash", pdf_actual == pdf_source["sha256"], pdf_actual, pdf_source["sha256"])

    contract = manifest["run_contract"]
    add(rows, "verifier_version", __version__ == manifest["sources"]["verifier"]["version"], __version__, manifest["sources"]["verifier"]["version"])
    add(rows, "primary_schema", primary.get("schema") == contract["primary_schema"], primary.get("schema"), contract["primary_schema"])
    add(rows, "independent_schema", independent.get("schema") == contract["independent_schema"], independent.get("schema"), contract["independent_schema"])
    add(rows, "primary_version", primary.get("script_version") == manifest["sources"]["primary"]["version"], primary.get("script_version"), manifest["sources"]["primary"]["version"])
    add(rows, "independent_version", independent.get("script_version") == manifest["sources"]["independent"]["version"], independent.get("script_version"), manifest["sources"]["independent"]["version"])
    add(rows, "primary_source_freshness", primary.get("source_sha256") == manifest["sources"]["primary"]["sha256"], primary.get("source_sha256"), manifest["sources"]["primary"]["sha256"])
    add(rows, "independent_source_freshness", independent.get("source_sha256") == manifest["sources"]["independent"]["sha256"], independent.get("source_sha256"), manifest["sources"]["independent"]["sha256"])
    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(rows, "independent_pass", independent.get("pass") is True, independent.get("pass"), True)
    add(rows, "primary_assertion_contract", primary.get("assertion_count") == contract["primary_assertions"], primary.get("assertion_count"), contract["primary_assertions"])
    add(rows, "independent_assertion_contract", independent.get("assertion_count") == contract["independent_assertions"], independent.get("assertion_count"), contract["independent_assertions"])
    add(rows, "primary_assertion_flags", len(primary.get("assertions", {})) == contract["primary_assertions"] and all(primary.get("assertions", {}).values()), [len(primary.get("assertions", {})), [key for key, value in primary.get("assertions", {}).items() if not value]], [contract["primary_assertions"], []])
    add(rows, "independent_assertion_flags", len(independent.get("assertions", {})) == contract["independent_assertions"] and all(independent.get("assertions", {}).values()), [len(independent.get("assertions", {})), [key for key, value in independent.get("assertions", {}).items() if not value]], [contract["independent_assertions"], []])
    add(rows, "shared_result_id", primary.get("result_id") == independent.get("result_id") == manifest["result_id"], [primary.get("result_id"), independent.get("result_id")], manifest["result_id"])
    add(rows, "shared_claim_id", primary.get("claim_id") == independent.get("claim_id") == manifest["claim_id"], [primary.get("claim_id"), independent.get("claim_id")], manifest["claim_id"])

    forbidden = manifest["independent_audit"]["forbidden_local_imports"]
    modules = imported_modules(independent_script)
    forbidden_found = [name for name in forbidden if any(module == name or module.endswith("." + name) for module in modules)]
    add(rows, "independent_nonimporting", not forbidden_found and independent.get("imports_primary") is False, forbidden_found, [])

    beta_primary = p["production_constants"]["beta_zero"]
    beta_independent = i["rational_constants"]["beta_float"]
    add(rows, "beta_zero_cross_route", abs(beta_primary - beta_independent) < 1e-14, [beta_primary, beta_independent], "equal within 1e-14")
    add(rows, "distance_constant_cross_route", abs(p["geometry_and_form"]["physical_distance_constant"] - i["rational_constants"]["distance_constant"]) < 1e-14, [p["geometry_and_form"]["physical_distance_constant"], i["rational_constants"]["distance_constant"]], "equal within 1e-14")
    add(rows, "M_moment_cross_route", abs(p["geometry_and_form"]["M_exponent"] - 10.0 / 3.0) < 1e-14 and i["cat_and_form"]["M_exponent_fraction"] == "10/3", [p["geometry_and_form"]["M_exponent"], i["cat_and_form"]["M_exponent_fraction"]], [10.0 / 3.0, "10/3"])
    add(rows, "eta_exponent_cross_route", abs(p["geometry_and_form"]["eta_negative_exponent"] - 11.0 / 6.0) < 1e-14 and i["cat_and_form"]["eta_exponent_fraction"] == "11/6", [p["geometry_and_form"]["eta_negative_exponent"], i["cat_and_form"]["eta_exponent_fraction"]], [11.0 / 6.0, "11/6"])
    add(rows, "zeta_exponent_cross_route", abs(p["geometry_and_form"]["zeta_negative_exponent"] - 0.5) < 1e-14 and i["cat_and_form"]["zeta_exponent_fraction"] == "1/2", [p["geometry_and_form"]["zeta_negative_exponent"], i["cat_and_form"]["zeta_exponent_fraction"]], [0.5, "1/2"])
    add(rows, "harvest_resolvent_cross_route", p["nonlinear_harvest"]["resolvent_residual"] < 1e-12 and i["harvest"]["maximum_residual"] < 1e-11, [p["nonlinear_harvest"]["resolvent_residual"], i["harvest"]["maximum_residual"]], "both below tolerance")
    add(rows, "full_score_cross_route", p["full_score"]["best_centered_difference_residual"] < 1e-8 and i["score_and_wick"]["score_residual"] < 1e-7, [p["full_score"]["best_centered_difference_residual"], i["score_and_wick"]["score_residual"]], "both below tolerance")
    add(rows, "gaussian_ell_decay", p["gaussian_tail"]["tail_rows"][-1]["ell_bound"] < p["gaussian_tail"]["tail_rows"][0]["ell_bound"] and i["gaussian_rates"]["rows"][-1]["ell"] < i["gaussian_rates"]["rows"][0]["ell"], True, True)
    add(rows, "gaussian_m_decay", p["gaussian_tail"]["tail_rows"][-1]["m_bound"] < p["gaussian_tail"]["tail_rows"][0]["m_bound"] and i["gaussian_rates"]["rows"][-1]["m"] < i["gaussian_rates"]["rows"][0]["m"], True, True)
    add(rows, "schur_completion_cross_route", p["scalar_schur"]["maximum_completion_residual"] < 1e-10 and i["scalar_schur"]["maximum_identity_residual"] == 0.0, [p["scalar_schur"]["maximum_completion_residual"], i["scalar_schur"]["maximum_identity_residual"]], "both below tolerance")
    add(rows, "schur_tip_tangent_failure", p["scalar_schur"]["tip_crossing_is_unbounded_below_in_b"] is True and i["scalar_schur"]["global_tangent_tip_sequence"][-1] < -100.0, [p["scalar_schur"]["tip_crossing_is_unbounded_below_in_b"], i["scalar_schur"]["global_tangent_tip_sequence"][-1]], [True, "less than -100"])
    add(rows, "gauge_beat_cross_route", p["gauge_beat"]["identity_residual"] < 1e-11 and i["gauge_beat"]["residual"] < 1e-11, [p["gauge_beat"]["identity_residual"], i["gauge_beat"]["residual"]], "both below tolerance")
    add(rows, "curvature_remainder_cross_route", abs(p["nonlinear_harvest"]["coefficient_curvature_remainder"]) > 1e-6 and abs(i["true_remainder"]["curvature_term"]) > 1e-6, [p["nonlinear_harvest"]["coefficient_curvature_remainder"], i["true_remainder"]["curvature_term"]], "both nonzero")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = text_contains(note_path, manifest["integrated_audit"]["proof_note_required_tokens"])
    add(rows, "proof_note_tokens", note_ok, note_missing, [])
    note_text = note_path.read_text(encoding="utf-8")
    add(rows, "proof_note_honesty", "Still open." in note_text and "No claim:" in note_text and "remains open" in note_text, True, True)

    pdf_path = REPO / pdf_source["path"]
    reader = PdfReader(str(pdf_path))
    pdf_texts = [(page.extract_text() or "") for page in reader.pages]
    add(rows, "pdf_page_count", len(reader.pages) == pdf_source["pages"], len(reader.pages), pdf_source["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == pdf_source["size_bytes"], pdf_path.stat().st_size, pdf_source["size_bytes"])
    add(rows, "pdf_nonblank_pages", all(len(text.strip()) > 80 for text in pdf_texts), [len(text.strip()) for text in pdf_texts], "each above 80 extracted characters")
    pdf_required = manifest["integrated_audit"]["pdf_required_tokens"]
    joined_pdf = "\n".join(pdf_texts)
    pdf_missing = [token for token in pdf_required if token not in joined_pdf]
    add(rows, "pdf_required_tokens", not pdf_missing, pdf_missing, [])
    boxes = [[float(value) for value in page.mediabox] for page in reader.pages]
    add(rows, "pdf_letter_boxes", all(abs(box[2] - 612.0) < 0.1 and abs(box[3] - 792.0) < 0.1 for box in boxes), boxes, "all 612x792 points")
    add(rows, "pdf_visual_qa_manifest", pdf_source["form_check"] == "PASS" and pdf_source["overfull_hbox_count"] == 0 and pdf_source["visual_qa"] == "PASS", [pdf_source["form_check"], pdf_source["overfull_hbox_count"], pdf_source["visual_qa"]], ["PASS", 0, "PASS"])

    surface_contracts = manifest["integrated_audit"]["surface_contracts"]
    for name, surface in surface_contracts.items():
        surface_path = REPO / surface["path"]
        ok, missing = text_contains(surface_path, surface["required_tokens"])
        add(rows, f"surface_{name}", ok, missing, [])

    claims_not = manifest["claims_not_established"]
    add(rows, "claims_not_established_false", all(value is False for value in claims_not.values()), claims_not, "all false")
    add(rows, "tier_unchanged", manifest["status"].startswith("T4 ") and "GLOBAL BALANCE OPEN" in manifest["status"], manifest["status"], "T4 and global balance open")
    add(rows, "successor_gate", manifest["consequence"]["next_subgate"] == "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE", manifest["consequence"]["next_subgate"], "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE")
    add(rows, "umbrella_open", manifest["consequence"]["umbrella_gate"] == "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE", manifest["consequence"]["umbrella_gate"], "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE")
    add(rows, "negative_result_registered", manifest["consequence"]["negative_result"] == "NG-2026-07-23-A13-ABSOLUTE-SCORE-AND-FULL-REMAINDER", manifest["consequence"]["negative_result"], "NG-2026-07-23-A13-ABSOLUTE-SCORE-AND-FULL-REMAINDER")

    integrated_expected = int(contract["integrated_assertions"])
    add(rows, "integrated_assertion_contract_preterminal", len(rows) + 1 == integrated_expected, len(rows) + 1, integrated_expected)
    passed = sum(row["status"] == "PASS" for row in rows)
    aggregate = int(primary["assertion_count"]) + int(independent["assertion_count"]) + len(rows)
    result = {
        "schema": contract["integrated_schema"],
        "verifier_version": __version__,
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_id"],
        "manifest_sha256": digest(manifest_path),
        "children": {"primary": primary, "independent": independent},
        "assertions": rows,
        "assertion_count": len(rows),
        "passed_assertions": passed,
        "aggregate_assertions": aggregate,
        "pass": passed == len(rows)
        and len(rows) == integrated_expected
        and aggregate == int(contract["aggregate_assertions"]),
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, result)
    print(f"PASS: primary ({primary['assertion_count']}/{primary['assertion_count']})")
    print(f"PASS: independent ({independent['assertion_count']}/{independent['assertion_count']})")
    print(f"ASSERTS: {aggregate}/{contract['aggregate_assertions']}")
    if result["pass"]:
        print("A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION-INTEGRATED-PASS")
    else:
        failures = [row["name"] for row in rows if row["status"] != "PASS"]
        print(f"FAIL: integrated {passed}/{len(rows)}; aggregate={aggregate}; failures={failures}")
    print(f"Evidence: {output_path}")
    return 0 if result["pass"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest, arguments.output)


if __name__ == "__main__":
    raise SystemExit(main())
