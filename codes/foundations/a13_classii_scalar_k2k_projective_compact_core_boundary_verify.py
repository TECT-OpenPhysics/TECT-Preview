#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-111 package."""

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
from decimal import Decimal
from pathlib import Path
from typing import Any

import sympy as sp
from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SCALAR-K2K-DEGENERATE-FACE-PROJECTIVE-COMPACT-CORE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_projective_compact_core_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_projective_compact_core_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-scalar-k2k-degenerate-face-projective-compact-core-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-scalar-k2k-degenerate-face-projective-compact-core-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_scalar_k2k_projective_compact_core_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-projective-compact-core-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-projective-compact-core-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-scalar-k2k-projective-compact-core-boundary/result.json"

PRIMARY_ASSERTION_ORACLE = 46
INDEPENDENT_ASSERTION_ORACLE = 35
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
}

NOTE_TOKENS = (
    "R-111",
    RESULT_ID,
    "evidence-anchor: theorem-2.1-degenerate-frequency-faces-all-q",
    "evidence-anchor: theorem-3.1-projective-large-amplitude-boundary",
    "evidence-anchor: proposition-3.2-positive-first-projective-correction",
    "evidence-anchor: theorem-4.1-phase-minimum-high-q-reduction",
    "evidence-anchor: theorem-4.2-bessel-and-factorized-tail-majorants",
    "evidence-anchor: proposition-5.1-separated-conditional-domination-nogos",
    "evidence-anchor: proposition-5.2-tilted-variance-monotonicity-nogo",
    "evidence-anchor: theorem-6.1-owner-map-scope",
    "NG-2026-07-28-A13-K2K-QUADRATIC-BESSEL-UPPER-DOMINATION",
    "NG-2026-07-28-A13-K2K-CONDITIONAL-SCALAR-TENSORIZATION",
    "NG-2026-07-28-A13-K2K-TILTED-VARIANCE-MONOTONICITY",
    "Sector A remain open",
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
    with tempfile.TemporaryDirectory(prefix="tect-r111-child-") as directory:
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

    # Hash and authority checks are deliberately completed before executable evidence runs.
    source_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": VERIFIER, "proof_note": NOTE}
    for label, path in source_paths.items():
        item = manifest.get("sources", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("hash", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("hash", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        item = manifest.get("child_results", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("hash", f"{label} result path", item.get("path") == relative, item.get("path"), relative)
        add("hash", f"{label} result digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))
    for label, relative in AUTHORITY_MANIFESTS.items():
        authority = manifest.get("authority", {}).get(label, {})
        path = REPO / relative
        add("authority", f"{label} manifest path", authority.get("manifest", {}).get("path") == relative, authority.get("manifest", {}).get("path"), relative)
        add("authority", f"{label} manifest digest", authority.get("manifest", {}).get("sha256") == digest(path), authority.get("manifest", {}).get("sha256"), digest(path))
    pdf_item = manifest.get("proof_pdf", {})
    pdf_relative = PDF.relative_to(REPO).as_posix()
    add("pdf", "PDF path", pdf_item.get("path") == pdf_relative, pdf_item.get("path"), pdf_relative)
    add("pdf", "PDF digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))

    preflight_failed = [row for row in rows if row["status"] != "PASS"]
    if preflight_failed:
        print("R-111 preflight hash/authority gate failed; child execution was not started.")
        for row in preflight_failed:
            print(f"FAIL [{row['group']}] {row['name']}: {row['actual']} != {row['expected']}")
        return 1

    children: dict[str, dict[str, Any]] = {}
    child_specs = (
        ("primary", PRIMARY, PRIMARY_RESULT, PRIMARY_ASSERTION_ORACLE, "tect/a13-scalar-k2k-projective-compact-core-boundary-primary/1.0"),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT, INDEPENDENT_ASSERTION_ORACLE, "tect/a13-scalar-k2k-projective-compact-core-boundary-independent/1.0"),
    )
    for label, script, pinned_path, expected_count, schema in child_specs:
        executed = execute_child(script)
        pinned = load_json(pinned_path)
        children[label] = pinned
        add("execution", f"{label} subprocess return", executed.get("returncode") == 0, executed.get("returncode"), 0)
        add("execution", f"{label} schema", executed.get("schema") == schema, executed.get("schema"), schema)
        add("execution", f"{label} pass contract", result_passes(executed, expected_count), executed.get("status"), "PASS")
        add("execution", f"{label} pinned pass contract", result_passes(pinned, expected_count), pinned.get("status"), "PASS")
        add("execution", f"{label} deterministic results", executed.get("results_sha256") == pinned.get("results_sha256"), executed.get("results_sha256"), pinned.get("results_sha256"))
        add("execution", f"{label} assertion-name stability", executed.get("assertion_names") == pinned.get("assertion_names"), len(executed.get("assertion_names", [])), len(pinned.get("assertion_names", [])))

    primary = children["primary"]
    independent = children["independent"]
    pr = primary.get("results", {})
    ir = independent.get("results", {})
    pv = primary.get("route_verdicts", {})
    iv = independent.get("route_verdicts", {})
    ps = pr.get("scale", {})
    ins = ir.get("normal_form", {})
    pf = pr.get("degenerate_face_theorem", {})
    inf = ir.get("degenerate_face_theorem", {})
    pp = pr.get("projective", {})
    ip = ir.get("projective", {})
    pc = pr.get("compact_core", {})
    it = ir.get("floor_tail", {})
    pb = pr.get("boundary_fixture", {})
    ib = ir.get("boundary", {})
    pt = pr.get("tilted_variance_route", {})
    i96 = ir.get("tilted_variance_route", {}).get("96", {})
    i128 = ir.get("tilted_variance_route", {}).get("128", {})

    add("cross", "normalized packet agreement", ps.get("normalized_packet") == ins.get("packet"), ps.get("normalized_packet"), ins.get("packet"))
    add("cross", "covariance square agreement", ps.get("normalized_covariance_square") == ins.get("covariance_square"), ps.get("normalized_covariance_square"), ins.get("covariance_square"))
    add("cross", "packet scaling weight", ps.get("packet_weight") == 2, ps.get("packet_weight"), 2)
    add("cross", "covariance-square scaling weight", ps.get("covariance_square_weight") == 4, ps.get("covariance_square_weight"), 4)
    add("cross", "three quotient shape parameters", ps.get("shape_parameters") == ["a=A^2/v", "r=w/v", "t=q*v^2"], ps.get("shape_parameters"), "a,r,t")
    add("cross", "face target coefficient agreement", pf.get("target_coefficient") == inf.get("target_coefficient"), pf.get("target_coefficient"), inf.get("target_coefficient"))
    add("cross", "tilted W mean identity", symbolic_equal(pf.get("tilted_W_mean"), inf.get("tilted_W_mean")), pf.get("tilted_W_mean"), inf.get("tilted_W_mean"))
    add("cross", "tilted W variance identity", symbolic_equal(pf.get("tilted_W_variance"), inf.get("tilted_W_variance")), pf.get("tilted_W_variance"), inf.get("tilted_W_variance"))
    add("cross", "w-zero face all-q", pf.get("w_zero_all_q") is True and inf.get("w_zero_all_q") is True, (pf.get("w_zero_all_q"), inf.get("w_zero_all_q")), "True/True")
    add("cross", "v-zero face all-q", pf.get("v_zero_all_q") is True and inf.get("v_zero_all_q") is True, (pf.get("v_zero_all_q"), inf.get("v_zero_all_q")), "True/True")
    add("cross", "projective limiting MGF agreement", pp.get("limiting_mgf") == ip.get("limiting_mgf"), pp.get("limiting_mgf"), ip.get("limiting_mgf"))
    add("cross", "projective limiting gap agreement", pp.get("limiting_gap") == ip.get("limiting_gap"), pp.get("limiting_gap"), ip.get("limiting_gap"))
    add("cross", "projective first correction agreement", pp.get("first_gap_correction") == ip.get("first_gap_correction"), pp.get("first_gap_correction"), ip.get("first_gap_correction"))
    add("cross", "projective positive numerator agreement", pp.get("first_gap_numerator") == ip.get("first_gap_numerator"), pp.get("first_gap_numerator"), ip.get("first_gap_numerator"))
    add("cross", "active floor cubic agreement", pc.get("active_floor_cubic") == it.get("active_cubic"), pc.get("active_floor_cubic"), it.get("active_cubic"))
    add("cross", "tail lower bound agreement", pc.get("tail_lower_bound") == it.get("tail_lower_bound"), pc.get("tail_lower_bound"), it.get("tail_lower_bound"))
    add("cross", "boundary log-MGF agreement", pb.get("log_mgf") == ib.get("log_mgf"), pb.get("log_mgf"), ib.get("log_mgf"))
    add("cross", "boundary gap agreement", pb.get("gap") == ib.get("gap"), pb.get("gap"), ib.get("gap"))
    ratio = Decimal(str(pb.get("ratio")))
    gap = Decimal(str(pb.get("gap")))
    add("cross", "boundary near-tight ratio", Decimal("0.99") < ratio < Decimal(1), ratio, "0.99<ratio<1")
    add("cross", "boundary positive small gap", Decimal(0) < gap < Decimal("1e-8"), gap, "0<gap<1e-8")
    add("cross", "primary tilted third moment negative", Decimal(str(pt.get("third_centered"))) < 0, pt.get("third_centered"), "<0")
    add("cross", "independent tilted third moments negative", float(i96.get("third_centered", 1)) < 0 and float(i128.get("third_centered", 1)) < 0, (i96.get("third_centered"), i128.get("third_centered")), "both <0")
    add("cross", "independent tilted variances positive", float(i96.get("variance", -1)) > 0 and float(i128.get("variance", -1)) > 0, (i96.get("variance"), i128.get("variance")), "both >0")
    add("cross", "tilted fixture remains inside target", Decimal(str(pt.get("target_gap"))) > 0, pt.get("target_gap"), ">0")
    add("cross", "degenerate faces route proved", pv.get("degenerate_frequency_faces") == iv.get("degenerate_frequency_faces") == "proved-all-q", (pv.get("degenerate_frequency_faces"), iv.get("degenerate_frequency_faces")), "proved-all-q")
    add("cross", "projective boundary advanced", pv.get("large_amplitude_projective_corner", "").startswith("advanced") and iv.get("projective_boundary") == "advanced", (pv.get("large_amplitude_projective_corner"), iv.get("projective_boundary")), "advanced/advanced")
    add("cross", "floor and tail routes advanced", pv.get("large_q_corner", "").startswith("advanced") and pv.get("certified_tail_enclosure", "").startswith("advanced") and iv.get("certified_tail_enclosure") == "advanced", (pv.get("large_q_corner"), pv.get("certified_tail_enclosure"), iv.get("certified_tail_enclosure")), "advanced")
    add("cross", "quadratic Bessel route failed", pv.get("quadratic_bessel_domination", "").startswith("failed") and iv.get("quadratic_bessel_domination") == "failed", (pv.get("quadratic_bessel_domination"), iv.get("quadratic_bessel_domination")), "failed/failed")
    add("cross", "conditional scalar route failed", pv.get("conditional_scalar_tensorization", "").startswith("failed") and iv.get("conditional_scalar_tensorization") == "failed", (pv.get("conditional_scalar_tensorization"), iv.get("conditional_scalar_tensorization")), "failed/failed")
    add("cross", "tilted variance route failed", pv.get("tilted_variance_monotonicity") == iv.get("tilted_variance_monotonicity") == "failed", (pv.get("tilted_variance_monotonicity"), iv.get("tilted_variance_monotonicity")), "failed/failed")
    add("cross", "mixed scalar all-q remains open", pv.get("bare_all_q_scalar_k2k", "").startswith("open") and iv.get("bare_all_q_scalar_k2k") == "open", (pv.get("bare_all_q_scalar_k2k"), iv.get("bare_all_q_scalar_k2k")), "open/open")
    add("cross", "production and Sector A remain open", pv.get("adapted_production_cluster") == iv.get("adapted_production_cluster") == "open" and pv.get("overlap_src") == "open" and pv.get("sector_a") == iv.get("sector_a") == "open", (pv.get("adapted_production_cluster"), pv.get("overlap_src"), pv.get("sector_a")), "open/open/open")

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"note token {token[:48]}", token in note_text, token in note_text, True)
    add("note", "REG owner scope preserved", "R-103 already closes REG" in note_text, "R-103 already closes REG" in note_text, True)
    add("note", "fixed-cutoff CORE owner preserved", "R-087 already" in note_text and "fixed-cutoff variational CORE" in note_text, "R-087/fixed-cutoff CORE" in note_text, True)
    add("note", "old R-085 route not reopened", "old R-085" in note_text and "not reopened" in note_text, "old R-085/not reopened" in note_text, True)
    add("note", "production boundary explicit", "full-A1" in note_text and "one-use source/sextic" in note_text and "OVERLAP" in note_text, "full-A1/one-use/OVERLAP" in note_text, True)
    add("note", "note exact child counts", "primary 46/46; independent 35/35" in note_text, "primary 46/46; independent 35/35" in note_text, True)

    reader = PdfReader(str(PDF))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    add("pdf", "PDF page count", len(reader.pages) == 11, len(reader.pages), 11)
    add("pdf", "PDF manifest page count", pdf_item.get("pages") == len(reader.pages), pdf_item.get("pages"), len(reader.pages))
    add("pdf", "PDF size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "PDF visual QA contract", pdf_item.get("visual_qa") == "PASS", pdf_item.get("visual_qa"), "PASS")
    add("pdf", "PDF form contract", pdf_item.get("form_check") == "PASS", pdf_item.get("form_check"), "PASS")
    add("pdf", "PDF overfull contract", pdf_item.get("overfull_hbox_count") == 0, pdf_item.get("overfull_hbox_count"), 0)
    add("pdf", "PDF extracted title", "Scalar k:2k degenerate-face theorem" in extracted, "Scalar k:2k degenerate-face theorem" in extracted, True)
    add("pdf", "PDF extracted face theorem", "theorem on both degenerate frequency faces" in extracted, "theorem on both degenerate frequency faces" in extracted, True)

    contract = manifest.get("run_contract", {})
    add("contract", "primary assertion contract", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertion contract", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary schema contract", contract.get("primary_schema") == child_specs[0][4], contract.get("primary_schema"), child_specs[0][4])
    add("contract", "independent schema contract", contract.get("independent_schema") == child_specs[1][4], contract.get("independent_schema"), child_specs[1][4])
    integrated_schema = "tect/a13-scalar-k2k-projective-compact-core-boundary-integrated/1.0"
    add("contract", "integrated schema contract", contract.get("integrated_schema") == integrated_schema, contract.get("integrated_schema"), integrated_schema)
    expected_command = str(sys.executable) + " " + VERIFIER.relative_to(REPO).as_posix()
    add("contract", "reproduction command", contract.get("command") == expected_command, contract.get("command"), expected_command)
    add("contract", "integrated assertion contract", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
    add("contract", "aggregate assertion contract", contract.get("aggregate_assertions") == PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE, contract.get("aggregate_assertions"), PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE)

    public_checks = {
        "claim card R-111": (CLAIM_DIR / "claim.md", "R-111"),
        "status R-111": (CLAIM_DIR / "status.json", "R-111"),
        "results ledger R-111": (REPO / "RESULTS-LEDGER.md", '<a id="r-111"></a>'),
        "quadratic Bessel negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-k2k-quadratic-bessel-upper-domination"),
        "conditional scalar negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-k2k-conditional-scalar-tensorization"),
        "tilted variance negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-k2k-tilted-variance-monotonicity"),
        "exploration first": (REPO / "explorations/log.jsonl", '"id":"EXP-000305"'),
        "exploration last": (REPO / "explorations/log.jsonl", '"id":"EXP-000312"'),
        "roadmap frontier": (REPO / "ROADMAP.md", "R-111"),
        "theorem-map frontier": (REPO / "governance/sector-a-theorem-map.json", "R-111"),
        "task frontier": (REPO / "TODO.md", "R-111"),
        "main proof line": (REPO / "theory/main-proof-line.md", "R-111"),
        "proof-evidence map": (REPO / "theory/proof-evidence-map.md", "R-111"),
        "proof-evidence JSON": (REPO / "verification/proof-evidence-map.json", "R-111"),
        "changelog R-111": (REPO / "CHANGELOG.md", "R-111"),
    }
    for name, (path, token) in public_checks.items():
        body = path.read_text(encoding="utf-8")
        add("public", name, token in body, token in body, True)

    claims_not = manifest.get("claims_not_established", {})
    for name in (
        "mixed_all_q_scalar_k2k",
        "uniform_projective_remainder",
        "compact_interior_certified",
        "full_a1_embedding",
        "adapted_production_cluster",
        "overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    ):
        add("scope", f"not established {name}", claims_not.get(name) is False, claims_not.get(name), False)
    consequence = manifest.get("consequence", {})
    add("scope", "proof not complete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("scope", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), "T4/T4")
    add("scope", "result ledger id", consequence.get("result_ledger_id") == "R-111", consequence.get("result_ledger_id"), "R-111")
    for name in (
        "degenerate_frequency_faces_all_q",
        "large_amplitude_projective_limit_positive",
        "first_inverse_amplitude_correction_positive",
        "exact_high_q_floor_reduction",
        "factorized_tail_majorant",
    ):
        add("scope", f"established {name}", consequence.get(name) is True, consequence.get(name), True)
    for name in (
        "mixed_all_q_scalar_k2k",
        "adapted_production_cluster",
        "full_overlap_src",
        "sector_a_closure",
        "reg_scope_newly_closed",
        "fixed_cutoff_core_newly_closed",
    ):
        add("scope", f"consequence remains false {name}", consequence.get(name) is False, consequence.get(name), False)

    pre_oracle_total = len(rows)
    if pre_oracle_total != INTEGRATED_ASSERTION_ORACLE:
        rows.append(
            {
                "group": "contract",
                "name": "integrated source assertion oracle",
                "status": "FAIL",
                "actual": str(pre_oracle_total),
                "expected": str(INTEGRATED_ASSERTION_ORACLE),
            }
        )
    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
    results = {
        "scale": pr.get("scale"),
        "degenerate_face_theorem": pr.get("degenerate_face_theorem"),
        "projective": pr.get("projective"),
        "compact_core": pr.get("compact_core"),
        "boundary_fixture": pr.get("boundary_fixture"),
        "separated_route_nogos": pr.get("separated_route_nogos"),
        "tilted_variance_route": pr.get("tilted_variance_route"),
    }
    payload: dict[str, Any] = {
        "schema": integrated_schema,
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": integrated_total,
        "assertions_passed": integrated_total - len(failed),
        "assertions_failed": len(failed),
        "assertions": rows,
        "assertion_names": [str(row["name"]) for row in rows],
        "aggregate_assertions": aggregate,
        "child_assertions": {"primary": PRIMARY_ASSERTION_ORACLE, "independent": INDEPENDENT_ASSERTION_ORACLE},
        "source_hashes": {"primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "verifier": digest(VERIFIER), "proof_note": digest(NOTE), "proof_pdf": digest(PDF)},
        "child_result_hashes": {"primary": digest(PRIMARY_RESULT), "independent": digest(INDEPENDENT_RESULT)},
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "route_verdicts": {
            "degenerate_frequency_faces": "proved-all-q",
            "large_amplitude_projective_corner": "advanced-pointwise-limit-and-first-correction",
            "large_q_corner": "advanced-exact-floor-cutoff",
            "certified_tail_enclosure": "advanced-factorized-majorant",
            "quadratic_bessel_domination": "failed-nonintegrable",
            "conditional_scalar_tensorization": "failed-negative-effective-coefficient",
            "tilted_variance_monotonicity": "failed",
            "mixed_all_q_scalar_k2k": "open-compact-interior",
            "uniform_projective_remainder": "open",
            "full_a1_embedding": "open",
            "adapted_production_cluster": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_A": "open",
        },
        "result_id": RESULT_ID,
    }
    atomic_json(OUTPUT, payload)
    print(f"Integrated R-111: {payload['assertions_passed']}/{payload['assertions_total']} PASS; aggregate {aggregate}/{aggregate}")
    if failed:
        for row in failed:
            print(f"FAIL [{row['group']}] {row['name']}: {row['actual']} != {row['expected']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
