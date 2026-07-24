#!/usr/bin/env python3
"""Integrated verifier for the A13 endpoint-lifted Schur/causal package."""

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
from pathlib import Path
from typing import Any

from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = (
    CLAIM / "classii_endpoint_lifted_schur_causal_grouping_reduction_manifest.json"
)
DEFAULT_OUTPUT = (
    CLAIM
    / "runs/2026-07-24-integrated-endpoint-lifted-schur-causal-grouping-reduction/result.json"
)


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


def text_contains(path: Path, tokens: list[str]) -> tuple[bool, list[str]]:
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in tokens if token not in content]
    return not missing, missing


def close(left: float, right: float, tolerance: float = 1.0e-13) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    preflight: list[tuple[str, str, str, str]] = []
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

    contract = manifest["run_contract"]
    primary = json.loads((REPO / contract["primary_output"]).read_text(encoding="utf-8"))
    independent = json.loads(
        (REPO / contract["independent_output"]).read_text(encoding="utf-8")
    )
    p = primary["computed"]
    i = independent["computed"]
    rows: list[dict[str, Any]] = []

    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            add(
                rows,
                f"{group}_{key}_hash",
                actual == source["sha256"],
                actual,
                source["sha256"],
            )
    add(rows, "proof_pdf_hash", pdf_actual == pdf_source["sha256"], pdf_actual, pdf_source["sha256"])

    add(
        rows,
        "manifest_schema",
        manifest.get("schema")
        == "tect/a13-classii-endpoint-lifted-schur-causal-grouping-reduction/1.0",
        manifest.get("schema"),
        "tect/a13-classii-endpoint-lifted-schur-causal-grouping-reduction/1.0",
    )
    add(rows, "verifier_version", __version__ == manifest["sources"]["verifier"]["version"], __version__, manifest["sources"]["verifier"]["version"])
    add(rows, "primary_schema", primary.get("schema") == contract["primary_schema"], primary.get("schema"), contract["primary_schema"])
    add(rows, "independent_schema", independent.get("schema") == contract["independent_schema"], independent.get("schema"), contract["independent_schema"])
    add(rows, "primary_version", primary.get("script_version") == manifest["sources"]["primary"]["version"], primary.get("script_version"), manifest["sources"]["primary"]["version"])
    add(rows, "independent_version", independent.get("script_version") == manifest["sources"]["independent"]["version"], independent.get("script_version"), manifest["sources"]["independent"]["version"])
    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(rows, "independent_pass", independent.get("pass") is True, independent.get("pass"), True)
    add(rows, "primary_assertion_contract", primary.get("assertion_count") == contract["primary_assertions"], primary.get("assertion_count"), contract["primary_assertions"])
    add(rows, "independent_assertion_contract", independent.get("assertion_count") == contract["independent_assertions"], independent.get("assertion_count"), contract["independent_assertions"])
    primary_rows = primary.get("assertions", [])
    independent_rows = independent.get("assertions", [])
    add(rows, "primary_assertion_flags", len(primary_rows) == contract["primary_assertions"] and all(row.get("pass") is True for row in primary_rows), [len(primary_rows), [row.get("name") for row in primary_rows if row.get("pass") is not True]], [contract["primary_assertions"], []])
    add(rows, "independent_assertion_flags", len(independent_rows) == contract["independent_assertions"] and all(row.get("pass") is True for row in independent_rows), [len(independent_rows), [row.get("name") for row in independent_rows if row.get("pass") is not True]], [contract["independent_assertions"], []])
    add(rows, "shared_result_id", primary.get("result_id") == independent.get("result_id") == manifest["result_id"], [primary.get("result_id"), independent.get("result_id")], manifest["result_id"])
    add(rows, "shared_claim_id", primary.get("claim") == independent.get("claim") == manifest["claim_id"], [primary.get("claim"), independent.get("claim")], manifest["claim_id"])

    forbidden = manifest["independent_audit"]["forbidden_local_imports"]
    modules = imported_modules(independent_script)
    forbidden_found = [
        name
        for name in forbidden
        if any(module == name or module.endswith("." + name) for module in modules)
    ]
    add(rows, "independent_nonimporting", not forbidden_found and independent.get("imports_primary") is False, forbidden_found, [])
    add(rows, "distinct_independent_inputs", primary["inputs"]["random_seed"] != independent["inputs"]["random_seed"] and p["fresh_noise_cross"]["order"] != i["fresh_noise_cross"]["order"], [primary["inputs"]["random_seed"], independent["inputs"]["random_seed"], p["fresh_noise_cross"]["order"], i["fresh_noise_cross"]["order"]], "distinct seeds and Hermite orders")

    plocal = p["local"]
    irandom = i["random"]
    add(rows, "lambda_cross_route", close(plocal["lambda_q"], irandom["lambda_q"]), [plocal["lambda_q"], irandom["lambda_q"]], "equal within 1e-13")
    add(rows, "theta_good_bad_cross_route", close(plocal["theta_good_bad"], irandom["theta_hash"]), [plocal["theta_good_bad"], irandom["theta_hash"]], "equal within 1e-13")
    add(rows, "c_good_bad_cross_route", close(plocal["c_good_bad"], irandom["c_hash"]), [plocal["c_good_bad"], irandom["c_hash"]], "equal within 1e-13")
    add(rows, "theta_global_cross_route", close(plocal["theta_global"], irandom["theta_star"]), [plocal["theta_global"], irandom["theta_star"]], "equal within 1e-13")
    add(rows, "c_global_cross_route", close(plocal["c_global"], irandom["c_star"]), [plocal["c_global"], irandom["c_star"]], "equal within 1e-13")
    add(rows, "local_identity_residuals", max(plocal["max_delta_residual"], plocal["max_secant_residual"], irandom["max_delta_residual"], irandom["max_secant_residual"]) < 1.0e-9, [plocal["max_delta_residual"], plocal["max_secant_residual"], irandom["max_delta_residual"], irandom["max_secant_residual"]], "all below 1e-9")
    add(rows, "good_bad_regions_populated", min(plocal["good_cases"], plocal["bad_cases"], irandom["good_count"], irandom["bad_count"]) > 0, [plocal["good_cases"], plocal["bad_cases"], irandom["good_count"], irandom["bad_count"]], "all positive")
    add(rows, "good_bad_global_margins", min(plocal["min_good_margin"], plocal["min_bad_margin"], plocal["min_global_margin"], irandom["min_good_margin"], irandom["min_bad_margin"], irandom["min_global_margin"]) > -2.0e-7, True, True)
    prot = p["rotating_kernel"]
    irot = i["rotating_kernel"]
    add(rows, "rotating_raw_zero", max(abs(prot["raw_secant"]), abs(irot["raw"])) < 1.0e-9, [prot["raw_secant"], irot["raw"]], 0.0)
    add(rows, "rotating_affine_nonzero", prot["affine_tangent"] > 1.0e-3 and irot["affine_tangent"] > 1.0e-3 and close(prot["affine_tangent"], prot["expected_affine_tangent"], 1.0e-11) and close(irot["affine_tangent"], irot["expected_affine"], 1.0e-11), [prot["affine_tangent"], irot["affine_tangent"]], "positive and equal to route oracle")
    add(rows, "endpoint_lift_kernel_cancels", max(abs(prot["endpoint_tangent"]), abs(prot["endpoint_jacobi"]), abs(prot["endpoint_curvature"]), abs(irot["endpoint_tangent"]), abs(irot["jacobi"]), abs(irot["curvature"])) < 1.0e-9, True, True)
    pcausal = p["coherent_causal"]
    icausal = i["coherent_causal"]
    add(rows, "causal_split_cross_route", max(abs(pcausal["max_split_residual"]), abs(pcausal["max_cross_residual"]), abs(icausal["split_max"])) < 1.0e-9, True, True)
    add(rows, "control_telescope_cross_route", max(abs(pcausal["control_telescoping_residual"]), abs(icausal["control_telescope"])) < 1.0e-9, True, True)
    add(rows, "mixed_telescope_cross_route", max(abs(pcausal["cross_telescoping_residual"]), abs(icausal["cross_telescope"])) < 1.0e-9, True, True)
    pgh = p["fresh_noise_cross"]
    igh = i["fresh_noise_cross"]
    add(rows, "fresh_noise_centering_cross_route", abs(pgh["signed_expectation"]) < 1.0e-9 and abs(igh["signed"]) < 1.0e-9 and pgh["absolute_expectation"] > 1.0e-5 and igh["absolute"] > 1.0e-5, [pgh, igh], "signed zero and absolute nonzero")
    pure = p["pure_control_separate_payment_nogo"]
    add(rows, "pure_control_separate_payment_nogo", pure["scaled_margin"] > 0.1 and pure["interaction_growth_power"] == pure["h2_growth_power"] == pure["sextic_growth_power"] == 6.0, pure, "positive margin and three derived N^6 powers")

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_ok, note_missing = text_contains(note_path, manifest["integrated_audit"]["proof_note_required_tokens"])
    add(rows, "proof_note_tokens", note_ok, note_missing, [])
    note_text = note_path.read_text(encoding="utf-8")
    add(
        rows,
        "proof_note_honesty",
        "Still open." in note_text
        and "No-overclaim statement:" in note_text
        and "remain open" in note_text,
        True,
        True,
    )
    add(rows, "proof_note_terminal_boundary", "|c_{J+1}|_Q^2-|c_{j_0}|_Q^2" in note_text and "sufficient next analytic target" in note_text, True, True)

    pdf_path = REPO / pdf_source["path"]
    add(rows, "pdf_signature", pdf_path.read_bytes()[:5] == b"%PDF-", pdf_path.read_bytes()[:5].decode("ascii", errors="replace"), "%PDF-")
    reader = PdfReader(str(pdf_path))
    pdf_texts = [(page.extract_text() or "") for page in reader.pages]
    add(rows, "pdf_page_count", len(reader.pages) == pdf_source["pages"], len(reader.pages), pdf_source["pages"])
    add(rows, "pdf_size", pdf_path.stat().st_size == pdf_source["size_bytes"], pdf_path.stat().st_size, pdf_source["size_bytes"])
    add(rows, "pdf_nonblank_pages", all(len(value.strip()) > 80 for value in pdf_texts), [len(value.strip()) for value in pdf_texts], "each above 80 extracted characters")
    joined_pdf = "\n".join(pdf_texts)
    pdf_missing = [token for token in manifest["integrated_audit"]["pdf_required_tokens"] if token not in joined_pdf]
    add(rows, "pdf_required_tokens", not pdf_missing, pdf_missing, [])
    boxes = [[float(value) for value in page.mediabox] for page in reader.pages]
    add(rows, "pdf_letter_boxes", all(abs(box[2] - 612.0) < 0.1 and abs(box[3] - 792.0) < 0.1 for box in boxes), boxes, "all 612x792 points")
    add(rows, "pdf_visual_qa_manifest", pdf_source["form_check"] == "PASS" and pdf_source["overfull_hbox_count"] == 0 and pdf_source["visual_qa"] == "PASS", [pdf_source["form_check"], pdf_source["overfull_hbox_count"], pdf_source["visual_qa"]], ["PASS", 0, "PASS"])

    for name, surface in manifest["integrated_audit"]["surface_contracts"].items():
        ok, missing = text_contains(REPO / surface["path"], surface["required_tokens"])
        add(rows, f"surface_{name}", ok, missing, [])

    claims_not = manifest["claims_not_established"]
    add(rows, "claims_not_established_false", all(value is False for value in claims_not.values()), claims_not, "all false")
    add(rows, "tier_and_open_boundary", manifest["status"].startswith("T4 ") and "OPEN" in manifest["status"], manifest["status"], "T4 and open boundary")
    add(rows, "successor_gate", manifest["consequence"]["next_subgate"] == "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE", manifest["consequence"]["next_subgate"], "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE")
    add(rows, "umbrella_open", manifest["consequence"]["umbrella_gate"] == "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE", manifest["consequence"]["umbrella_gate"], "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE")
    add(rows, "negative_result_registered", manifest["consequence"]["negative_result"] == "NG-2026-07-24-A13-AFFINE-SCHUR-AND-PURE-CONTROL-PAYMENT", manifest["consequence"]["negative_result"], "NG-2026-07-24-A13-AFFINE-SCHUR-AND-PURE-CONTROL-PAYMENT")
    add(rows, "result_ledger_registered", manifest["consequence"]["result_ledger_id"] == "R-069", manifest["consequence"]["result_ledger_id"], "R-069")

    expected_integrated = int(contract["integrated_assertions"])
    add(rows, "integrated_assertion_contract_preterminal", len(rows) + 1 == expected_integrated, len(rows) + 1, expected_integrated)
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
        and len(rows) == expected_integrated
        and aggregate == int(contract["aggregate_assertions"]),
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, result)
    print(f"PASS: primary ({primary['assertion_count']}/{primary['assertion_count']})")
    print(f"PASS: independent ({independent['assertion_count']}/{independent['assertion_count']})")
    print(f"ASSERTS: {aggregate}/{contract['aggregate_assertions']}")
    if result["pass"]:
        print("A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION-INTEGRATED-PASS")
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
