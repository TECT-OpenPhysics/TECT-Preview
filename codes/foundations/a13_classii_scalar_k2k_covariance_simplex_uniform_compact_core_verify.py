#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-112 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp
from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SCALAR-K2K-COVARIANCE-SIMPLEX-UNIFORM-PROJECTIVE-COMPACT-CORE-REDUCTION"
NEGATIVE_ID = "NG-2026-07-28-A13-K2K-ALL-ORDER-PROJECTIVE-COEFFICIENT-POSITIVITY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_covariance_simplex_uniform_compact_core.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_covariance_simplex_uniform_compact_core_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-scalar-k2k-covariance-simplex-uniform-projective-compact-core-reduction-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-scalar-k2k-covariance-simplex-uniform-projective-compact-core-reduction-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_scalar_k2k_covariance_simplex_uniform_compact_core_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-covariance-simplex-uniform-compact-core/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-covariance-simplex-uniform-compact-core/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-scalar-k2k-covariance-simplex-uniform-compact-core/result.json"

# Declared test oracles, not derived theorem constants.
PRIMARY_ASSERTION_ORACLE = 69
INDEPENDENT_ASSERTION_ORACLE = 50
INTEGRATED_ASSERTION_ORACLE = 152

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r087": f"claims/{CLAIM}/classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
    "r101": f"claims/{CLAIM}/classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r108": f"claims/{CLAIM}/classii_complete_cluster_quotient_carleson_frontier_manifest.json",
    "r109": f"claims/{CLAIM}/classii_square_first_pair_score_transfer_filtration_boundary_manifest.json",
    "r110": f"claims/{CLAIM}/classii_random_w_skorohod_diagonal_crossmode_boundary_manifest.json",
    "r111": f"claims/{CLAIM}/classii_scalar_k2k_projective_compact_core_boundary_manifest.json",
}

NOTE_TOKENS = (
    "R-112",
    RESULT_ID,
    "evidence-anchor: theorem-2.1-global-floor-compact-semialgebraic-core",
    "evidence-anchor: theorem-2.2-uniform-radial-tail",
    "evidence-anchor: theorem-3.1-uniform-projective-expansion",
    "evidence-anchor: corollary-3.2-uniform-large-amplitude-all-q",
    "evidence-anchor: theorem-4.1-origin-bernstein-mgf-patch",
    "evidence-anchor: proposition-4.2-face-and-interior-reduction",
    "evidence-anchor: proposition-5.1-third-projective-coefficient-nogo",
    NEGATIVE_ID,
    "strict mixed core still requires",
    "Sector A are not closed",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def canonical_results_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(record.get("results"), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def result_passes(record: dict[str, Any], expected: int) -> bool:
    assertions = record.get("assertions")
    names = record.get("assertion_names")
    return (
        record.get("status") == "PASS"
        and record.get("assertions_total") == expected
        and record.get("assertions_passed") == expected
        and record.get("assertions_failed") == 0
        and isinstance(assertions, list)
        and len(assertions) == expected
        and isinstance(names, list)
        and len(names) == expected
        and len(set(map(str, names))) == expected
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertions)
        and record.get("results_sha256") == canonical_results_hash(record)
    )


def execute_child(script: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-r112-child-") as directory:
        output = Path(directory) / "result.json"
        process = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if process.returncode != 0:
            return {"execution_error": process.stderr or process.stdout, "returncode": process.returncode}
        record = load_json(output)
        record["returncode"] = process.returncode
        record["stdout"] = process.stdout.strip()
        return record


def symbolic_equal(left: object, right: object) -> bool:
    try:
        return sp.simplify(sp.sympify(str(left)) - sp.sympify(str(right))) == 0
    except (TypeError, ValueError, sp.SympifyError):
        return False


def compact_string(value: object) -> str:
    return "".join(str(value).replace("^", "**").split())


def main() -> int:
    rows: list[dict[str, object]] = []

    def add(group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    manifest = load_json(MANIFEST)
    pinned_primary = load_json(PRIMARY_RESULT)
    pinned_independent = load_json(INDEPENDENT_RESULT)

    # Hash and authority checks precede executable evidence runs.
    source_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": VERIFIER,
        "proof_note": NOTE,
    }
    for label, path in source_paths.items():
        item = manifest.get("sources", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("preflight", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("preflight", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    child_paths = {"primary": PRIMARY_RESULT, "independent": INDEPENDENT_RESULT}
    for label, path in child_paths.items():
        item = manifest.get("child_results", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("preflight", f"{label} result path", item.get("path") == relative, item.get("path"), relative)
        add("preflight", f"{label} result digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    for label, relative in AUTHORITY_MANIFESTS.items():
        item = manifest.get("authority", {}).get(label, {}).get("manifest", {})
        path = REPO / relative
        add("authority", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("authority", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    pdf_item = manifest.get("proof_pdf", {})
    pdf_relative = PDF.relative_to(REPO).as_posix()
    add("preflight", "PDF path", pdf_item.get("path") == pdf_relative, pdf_item.get("path"), pdf_relative)
    add("preflight", "PDF digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))

    preflight_failed = [row for row in rows if row["status"] != "PASS"]
    if preflight_failed:
        print("R-112 preflight hash/authority gate failed; child execution was not started.")
        for row in preflight_failed:
            print(f"  {row['group']}::{row['name']}: {row['actual']} != {row['expected']}")
        return 1

    executed_primary = execute_child(PRIMARY)
    executed_independent = execute_child(INDEPENDENT)
    child_contracts = (
        ("primary", pinned_primary, executed_primary, PRIMARY_ASSERTION_ORACLE, manifest["run_contract"]["primary_schema"]),
        ("independent", pinned_independent, executed_independent, INDEPENDENT_ASSERTION_ORACLE, manifest["run_contract"]["independent_schema"]),
    )
    for label, pinned, executed, expected, schema in child_contracts:
        add("execution", f"{label} pinned PASS contract", result_passes(pinned, expected), pinned.get("assertions_total"), expected)
        add("execution", f"{label} fresh PASS contract", result_passes(executed, expected), executed.get("assertions_total"), expected)
        add("execution", f"{label} schema", pinned.get("schema") == schema, pinned.get("schema"), schema)
        add("execution", f"{label} deterministic results", executed.get("results_sha256") == pinned.get("results_sha256"), executed.get("results_sha256"), pinned.get("results_sha256"))
        add("execution", f"{label} assertion-name stability", executed.get("assertion_names") == pinned.get("assertion_names"), len(executed.get("assertion_names", [])), len(pinned.get("assertion_names", [])))

    primary = pinned_primary["results"]
    independent = pinned_independent["results"]
    p_normal, i_normal = primary["compact_normal_form"], independent["compact_normal_form"]
    add("cross", "covariance square", symbolic_equal(p_normal["covariance_square"], i_normal["covariance_square"]), p_normal["covariance_square"], i_normal["covariance_square"])
    add("cross", "local margin", symbolic_equal(p_normal["local_margin"], i_normal["local_margin"]), p_normal["local_margin"], i_normal["local_margin"])
    add("cross", "local lower", p_normal["local_margin_uniform_lower"] == i_normal["local_margin_uniform_lower"] == "1/100", (p_normal["local_margin_uniform_lower"], i_normal["local_margin_uniform_lower"]), "1/100")

    p_projective, i_projective = primary["uniform_projective"], independent["uniform_projective"]
    for key in (
        "second_bernstein_degree",
        "second_bernstein_min_coefficients",
        "second_margin_reserve_bernstein_min_coefficients",
        "second_global_lower",
    ):
        add("cross", f"projective {key}", p_projective[key] == i_projective[key], p_projective[key], i_projective[key])
    add("cross", "projective second local limit", symbolic_equal(p_projective["second_local_limit"], i_projective["second_local_limit"]), p_projective["second_local_limit"], i_projective["second_local_limit"])
    add("cross", "projective remainder normalized", p_projective["uniform_remainder"].replace("Y(y", "X(x") == i_projective["uniform_remainder"], p_projective["uniform_remainder"], i_projective["uniform_remainder"])

    p_core, i_core = primary["compact_core"], independent["compact_core"]
    for key in (
        "global_tau_cutoff",
        "residual_semialgebraic_condition",
        "residual_box",
        "radial_tail_radius",
        "radial_tail_worst_bound",
        "origin_patch_condition",
        "interval_certificate_complete",
    ):
        add("cross", f"compact core {key}", p_core[key] == i_core[key], p_core[key], i_core[key])
    add("cross", "global floor", compact_string(p_core["global_floor"]) == compact_string(i_core["global_floor"]), p_core["global_floor"], i_core["global_floor"])
    add("cross", "covariance floor", compact_string(p_core["covariance_square_floor"]) == compact_string(i_core["covariance_square_floor"]), p_core["covariance_square_floor"], i_core["covariance_square_floor"])
    tail_value = sp.Float(p_core["radial_tail_worst_bound"], 60)
    add("cross", "radial tail declared strict decimal", tail_value < sp.Rational(1091, 10**20), tail_value, "<1.091e-17")

    p_nogo, i_nogo = primary["all_order_projective_nogo"], independent["all_order_projective_nogo"]
    add("cross", "third coefficient exact", p_nogo["third_coefficient"] == i_nogo["third_coefficient"], p_nogo["third_coefficient"], i_nogo["third_coefficient"])
    add("cross", "third coefficient negative", p_nogo["third_coefficient_negative"] is i_nogo["third_coefficient_negative"] is True, (p_nogo["third_coefficient_negative"], i_nogo["third_coefficient_negative"]), True)
    add("cross", "negative coefficient is not target counterexample", p_nogo["target_counterexample"] is i_nogo["target_counterexample"] is False, (p_nogo["target_counterexample"], i_nogo["target_counterexample"]), False)
    add("cross", "existential large-amplitude theorem", primary["uniform_large_amplitude"]["existential_all_q_threshold"] is True, primary["uniform_large_amplitude"]["existential_all_q_threshold"], True)
    add("cross", "effective threshold open", primary["uniform_large_amplitude"]["effective_threshold_certified"] is False, primary["uniform_large_amplitude"]["effective_threshold_certified"], False)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"token {token}", token in note_text, token in note_text, True)

    reader = PdfReader(str(PDF))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    add("pdf", "page count", len(reader.pages) == 9, len(reader.pages), 9)
    add("pdf", "manifest page count", pdf_item.get("pages") == len(reader.pages), pdf_item.get("pages"), len(reader.pages))
    add("pdf", "size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "visual QA", pdf_item.get("visual_qa") == "PASS", pdf_item.get("visual_qa"), "PASS")
    add("pdf", "form check", pdf_item.get("form_check") == "PASS", pdf_item.get("form_check"), "PASS")
    add("pdf", "zero overfull", pdf_item.get("overfull_hbox_count") == 0, pdf_item.get("overfull_hbox_count"), 0)
    add("pdf", "no forms", not bool(reader.get_fields()), bool(reader.get_fields()), False)
    add("pdf", "title extracted", "Scalar k:2k covariance-simplex" in extracted, "Scalar k:2k covariance-simplex" in extracted, True)
    add("pdf", "R-112 extracted", "R-112" in extracted, "R-112" in extracted, True)
    add("pdf", "no literal qquad debris", "qquad" not in extracted, "qquad" in extracted, False)

    contract = manifest.get("run_contract", {})
    add("contract", "primary assertions", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertions", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary output", contract.get("primary_output") == PRIMARY_RESULT.relative_to(REPO).as_posix(), contract.get("primary_output"), PRIMARY_RESULT.relative_to(REPO).as_posix())
    add("contract", "independent output", contract.get("independent_output") == INDEPENDENT_RESULT.relative_to(REPO).as_posix(), contract.get("independent_output"), INDEPENDENT_RESULT.relative_to(REPO).as_posix())
    add("contract", "integrated output", contract.get("integrated_output") == OUTPUT.relative_to(REPO).as_posix(), contract.get("integrated_output"), OUTPUT.relative_to(REPO).as_posix())
    add("contract", "reproduction command", contract.get("command") == r"E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/a13_classii_scalar_k2k_covariance_simplex_uniform_compact_core_verify.py", contract.get("command"), "canonical command")

    public_checks = {
        "claim card": (CLAIM_DIR / "claim.md", "R-112"),
        "status card": (CLAIM_DIR / "status.json", "R-112"),
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-112"></a>'),
        "negative registry": (REPO / "negative-results/registry.md", NEGATIVE_ID),
        "exploration ledger first": (REPO / "explorations/log.jsonl", '"id":"EXP-000313"'),
        "exploration ledger last": (REPO / "explorations/log.jsonl", '"id":"EXP-000317"'),
        "roadmap": (REPO / "ROADMAP.md", "R-112"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", "R-112"),
        "todo": (REPO / "TODO.md", "R-112"),
        "main proof line": (REPO / "theory/main-proof-line.md", "R-112"),
        "proof map markdown": (REPO / "theory/proof-evidence-map.md", "R-112"),
        "proof map json": (REPO / "verification/proof-evidence-map.json", "R-112"),
        "changelog": (REPO / "CHANGELOG.md", "R-112 covariance-simplex uniform projective compact-core reduction"),
    }
    for name, (path, token) in public_checks.items():
        body = path.read_text(encoding="utf-8")
        add("public", name, token in body, token in body, True)

    add("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "result ledger id", manifest.get("consequence", {}).get("result_ledger_id") == "R-112", manifest.get("consequence", {}).get("result_ledger_id"), "R-112")
    add("manifest", "negative record", manifest.get("negative_results") == [NEGATIVE_ID], manifest.get("negative_results"), [NEGATIVE_ID])
    add("manifest", "exploration range", manifest.get("explorations") == [f"EXP-{index:06d}" for index in range(313, 318)], manifest.get("explorations"), "EXP-000313--EXP-000317")
    add("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("manifest", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), "T4/T4")

    consequence = manifest.get("consequence", {})
    for name in (
        "covariance_simplex_compactification",
        "uniform_projective_remainder",
        "first_inverse_amplitude_coefficient_nonnegative",
        "second_inverse_amplitude_coefficient_positive",
        "existential_uniform_large_amplitude_all_q",
        "effective_compact_semialgebraic_domain",
        "uniform_radial_tail",
        "origin_patch",
        "slice_wise_face_patches",
    ):
        add("scope", f"established {name}", consequence.get(name) is True, consequence.get(name), True)
    for name in (
        "effective_large_amplitude_threshold",
        "strict_mixed_core_interval_certificate",
        "mixed_all_q_scalar_k2k",
        "full_a1_embedding",
        "adapted_production_cluster",
        "full_overlap_src",
        "nelson",
        "sector_a_closure",
        "reg_scope_newly_closed",
        "fixed_cutoff_core_newly_closed",
    ):
        add("scope", f"consequence remains false {name}", consequence.get(name) is False, consequence.get(name), False)
    for name, value in manifest.get("claims_not_established", {}).items():
        add("scope", f"not established {name}", value is False, value, False)
    add("scope", "all-order positivity false", consequence.get("all_order_coefficientwise_positivity") is False, consequence.get("all_order_coefficientwise_positivity"), False)
    add("scope", "target counterexample false", consequence.get("target_counterexample") is False, consequence.get("target_counterexample"), False)

    if INTEGRATED_ASSERTION_ORACLE:
        predicted_total = len(rows) + 3
        add("contract", "integrated assertion oracle", predicted_total == INTEGRATED_ASSERTION_ORACLE, predicted_total, INTEGRATED_ASSERTION_ORACLE)
        add("contract", "manifest integrated assertions", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
        add("contract", "aggregate assertions", contract.get("aggregate_assertions") == PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE, contract.get("aggregate_assertions"), PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE)

    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
    results = {
        "result_id": RESULT_ID,
        "preflight_hash_gate": "PASS",
        "children_reexecuted": True,
        "child_results_match_pins": not any(row["status"] != "PASS" for row in rows if row["group"] == "execution"),
        "covariance_simplex_cross_audit": "PASS" if not failed else "FAIL",
        "proof_pdf_pages": len(reader.pages),
        "strict_mixed_core_interval_certificate": False,
        "mixed_all_q_scalar_k2k": False,
        "target_counterexample": False,
        "full_a1_embedding": False,
        "sector_a_closure": False,
    }
    payload: dict[str, Any] = {
        "schema": "tect/a13-scalar-k2k-covariance-simplex-uniform-compact-core-integrated/1.0",
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": integrated_total,
        "assertions_passed": integrated_total - len(failed),
        "assertions_failed": len(failed),
        "assertions": rows,
        "assertion_names": [f"{row['group']}::{row['name']}" for row in rows],
        "aggregate_assertions": aggregate,
        "child_assertions": {"primary": PRIMARY_ASSERTION_ORACLE, "independent": INDEPENDENT_ASSERTION_ORACLE},
        "source_hashes": {label: digest(path) for label, path in {**source_paths, "proof_pdf": PDF}.items()},
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
    }
    atomic_json(OUTPUT, payload)
    for row in failed:
        print(f"FAIL {row['group']}::{row['name']}: {row['actual']} != {row['expected']}")
    print(f"Integrated R-112: {payload['assertions_passed']}/{integrated_total} PASS; aggregate {aggregate}/{aggregate}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
