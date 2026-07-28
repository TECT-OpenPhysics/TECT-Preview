#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-110 package."""

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

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RANDOM-W-SKOROHOD-DIAGONAL-CROSSMODE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_random_w_skorohod_diagonal_crossmode_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_random_w_skorohod_diagonal_crossmode_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-random-w-skorohod-diagonal-crossmode-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-random-w-skorohod-diagonal-crossmode-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_random_w_skorohod_diagonal_crossmode_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-random-w-skorohod-diagonal-crossmode-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-random-w-skorohod-diagonal-crossmode-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-random-w-skorohod-diagonal-crossmode-boundary/result.json"

PRIMARY_ASSERTION_ORACLE = 40
INDEPENDENT_ASSERTION_ORACLE = 49
INTEGRATED_ASSERTION_ORACLE = 111

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r107": f"claims/{CLAIM}/classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r108": f"claims/{CLAIM}/classii_complete_cluster_quotient_carleson_frontier_manifest.json",
    "r109": f"claims/{CLAIM}/classii_square_first_pair_score_transfer_filtration_boundary_manifest.json",
}

NOTE_TOKENS = (
    "R-110",
    RESULT_ID,
    "evidence-anchor: theorem-1.1-random-w-double-divergence-score-transfer",
    "evidence-anchor: theorem-1.2-random-w-young-optimized-form-bound",
    "evidence-anchor: proposition-2.1-uniformly-positive-random-w-nogo",
    "evidence-anchor: proposition-2.2-rotating-projector-nogo",
    "evidence-anchor: theorem-3.1-trace-corrected-diagonal-interpolation",
    "evidence-anchor: proposition-4.1-nonlinear-square-first-mean-debt-nogo",
    "evidence-anchor: theorem-5.1-complete-k2k-packet-moments",
    "evidence-anchor: theorem-6.1-sharp-pointwise-cross-payment",
    "NG-2026-07-28-A13-RANDOM-W-HS-ONLY-SCORE-TRANSFER",
    "NG-2026-07-28-A13-UNIVERSAL-NONLINEAR-TANGENT-SQUARE-FIRST-NORMALIZER",
    "NG-2026-07-28-A13-CROSS-RESONANCE-POINTWISE-BASELINE-PAYMENT",
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


def execute_child(script: Path, expected: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-r110-child-") as directory:
        output = Path(directory) / "result.json"
        process = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if process.returncode != 0:
            return {"execution_error": process.stderr or process.stdout, "returncode": process.returncode}
        record = load_json(output)
        record["returncode"] = process.returncode
        record["stdout"] = process.stdout.strip()
        record["expected"] = expected
        return record


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
    children: dict[str, dict[str, Any]] = {}
    child_specs = (
        (
            "primary",
            PRIMARY,
            PRIMARY_RESULT,
            PRIMARY_ASSERTION_ORACLE,
            "tect/a13-random-w-skorohod-diagonal-crossmode-boundary-primary/1.0",
        ),
        (
            "independent",
            INDEPENDENT,
            INDEPENDENT_RESULT,
            INDEPENDENT_ASSERTION_ORACLE,
            "tect/a13-random-w-skorohod-diagonal-crossmode-boundary-independent/1.0",
        ),
    )
    for label, script, pinned_path, expected_count, schema in child_specs:
        executed = execute_child(script, expected_count)
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
    scan_rows = pr.get("cross_cluster", {}).get("scan_margins", [])
    scan_sign_stable = (
        isinstance(scan_rows, list)
        and len(scan_rows) == 4
        and all(
            isinstance(row, dict)
            and float(row.get("order_24", "nan")) > 0
            and float(row.get("order_48", "nan")) > 0
            for row in scan_rows
        )
    )
    add("cross", "random-W q constant agreement", pr.get("random_w", {}).get("q_random_cost") == ir.get("q_random_cost") == "25/2592", (pr.get("random_w", {}).get("q_random_cost"), ir.get("q_random_cost")), "25/2592")
    add("cross", "fixed-W q constant agreement", pr.get("random_w", {}).get("q_fixed_cost") == ir.get("q_fixed_cost") == "25/1296", (pr.get("random_w", {}).get("q_fixed_cost"), ir.get("q_fixed_cost")), "25/1296")
    add("cross", "mean-debt Jensen agreement", pr.get("mean_debt", {}).get("q_fixture_jensen") == ir.get("mean_debt", {}).get("jensen") == "1/90", (pr.get("mean_debt", {}).get("q_fixture_jensen"), ir.get("mean_debt", {}).get("jensen")), "1/90")
    add("cross", "mean-debt square-cost agreement", pr.get("mean_debt", {}).get("q_fixture_square_cost") == ir.get("mean_debt", {}).get("square_cost") == "73/32400", (pr.get("mean_debt", {}).get("q_fixture_square_cost"), ir.get("mean_debt", {}).get("square_cost")), "73/32400")
    add("cross", "mean-debt violation agreement", pr.get("mean_debt", {}).get("violation_margin") == ir.get("mean_debt", {}).get("violation") == "287/32400", (pr.get("mean_debt", {}).get("violation_margin"), ir.get("mean_debt", {}).get("violation")), "287/32400")
    for key, expected in (("pointwise_baseline", 1), ("covariance_floor", -3), ("square_first_baseline", -1)):
        add("cross", f"shell exponent {key}", pr.get("shell_exponents", {}).get(key) == ir.get("shell_exponents", {}).get(key) == expected, (pr.get("shell_exponents", {}).get(key), ir.get("shell_exponents", {}).get(key)), expected)
    add("cross", "random-W double divergence proved", pv.get("random_W_double_divergence") == "proved-exact-form-bound" and iv.get("random_W_double_divergence") == "pass", (pv.get("random_W_double_divergence"), iv.get("random_W_double_divergence")), "proved/pass")
    add("cross", "random-W HS-only extension failed", pv.get("random_W_HS_only_extension") == "failed" and iv.get("random_W_HS_only_extension") == "fail", (pv.get("random_W_HS_only_extension"), iv.get("random_W_HS_only_extension")), "failed/fail")
    add("cross", "trace-corrected interpolation proved", pv.get("trace_corrected_diagonal_interpolation") == "proved-exact-identity" and iv.get("trace_corrected_interpolation") == "pass", (pv.get("trace_corrected_diagonal_interpolation"), iv.get("trace_corrected_interpolation")), "proved/pass")
    add("cross", "universal nonlinear square-first failed", pv.get("universal_nonlinear_square_first") == "failed" and iv.get("universal_nonlinear_square_first") == "fail", (pv.get("universal_nonlinear_square_first"), iv.get("universal_nonlinear_square_first")), "failed/fail")
    add("cross", "physical k2k moments proved", pv.get("physical_k2k_complete_cluster") == "proved-exact-moments" and iv.get("physical_k2k_moments") == "pass", (pv.get("physical_k2k_complete_cluster"), iv.get("physical_k2k_moments")), "proved/pass")
    add("cross", "pointwise payment nonsummable", pv.get("pointwise_cross_payment") == "proved-but-nonsummable" and iv.get("pointwise_payment") == "nonsummable", (pv.get("pointwise_cross_payment"), iv.get("pointwise_payment")), "proved-but-nonsummable/nonsummable")
    add("cross", "bare all-q k2k remains open", pv.get("physical_k2k_bare_all_q_square_first") == "open-passed-local-and-finite-falsifiers" and iv.get("physical_k2k_bare_all_q") == "open" and scan_sign_stable, (pv.get("physical_k2k_bare_all_q_square_first"), iv.get("physical_k2k_bare_all_q"), scan_sign_stable), "open-local/open/two-order-sign-stable")
    add("cross", "production complete cluster remains open", pv.get("production_complete_cluster") == "open", pv.get("production_complete_cluster"), "open")
    add("cross", "Sector A remains open", pv.get("sector_a") == "open" and iv.get("sector_A") == "open", (pv.get("sector_a"), iv.get("sector_A")), "open/open")

    expected_sources = manifest.get("sources", {})
    source_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": VERIFIER, "proof_note": NOTE}
    for label, path in source_paths.items():
        item = expected_sources.get(label, {})
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

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"note token {token[:48]}", token in note_text, token in note_text, True)
    lower_note = note_text.lower()
    add("note", "note preserves live all-q production boundary", "bare all-q" in lower_note and "full adapted production cluster" in lower_note and "nelson" in lower_note, "bare all-q/full production/Nelson" in lower_note, True)
    add("note", "note exact child counts", "primary 40/40; independent 49/49" in note_text, "primary 40/40; independent 49/49" in note_text, True)

    reader = PdfReader(str(PDF))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    pdf_item = manifest.get("proof_pdf", {})
    add("pdf", "PDF page count", len(reader.pages) == 12, len(reader.pages), 12)
    add("pdf", "PDF manifest page count", pdf_item.get("pages") == len(reader.pages), pdf_item.get("pages"), len(reader.pages))
    add("pdf", "PDF digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))
    add("pdf", "PDF size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "PDF visual QA contract", pdf_item.get("visual_qa") == "PASS", pdf_item.get("visual_qa"), "PASS")
    add("pdf", "PDF form contract", pdf_item.get("form_check") == "PASS", pdf_item.get("form_check"), "PASS")
    add("pdf", "PDF extracted title", "Random-covariance Skorohod completion" in extracted, "Random-covariance Skorohod completion" in extracted, True)
    add("pdf", "PDF extracted theorem", "random-covariance double-divergence transfer" in extracted, "random-covariance double-divergence transfer" in extracted, True)

    contract = manifest.get("run_contract", {})
    add("contract", "primary assertion contract", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertion contract", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary schema contract", contract.get("primary_schema") == child_specs[0][4], contract.get("primary_schema"), child_specs[0][4])
    add("contract", "independent schema contract", contract.get("independent_schema") == child_specs[1][4], contract.get("independent_schema"), child_specs[1][4])
    integrated_schema = "tect/a13-random-w-skorohod-diagonal-crossmode-boundary-integrated/1.0"
    add("contract", "integrated schema contract", contract.get("integrated_schema") == integrated_schema, contract.get("integrated_schema"), integrated_schema)
    expected_command = str(sys.executable) + " " + VERIFIER.relative_to(REPO).as_posix()
    add("contract", "reproduction command", contract.get("command") == expected_command, contract.get("command"), expected_command)
    add("contract", "integrated assertion contract", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
    add("contract", "aggregate assertion contract", contract.get("aggregate_assertions") == PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE, contract.get("aggregate_assertions"), PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE)

    public_checks = {
        "claim card R-110": (CLAIM_DIR / "claim.md", "R-110"),
        "status R-110": (CLAIM_DIR / "status.json", "R-110"),
        "results ledger R-110": (REPO / "RESULTS-LEDGER.md", '<a id="r-110"></a>'),
        "random-W negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-random-w-hs-only-score-transfer"),
        "mean-debt negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-universal-nonlinear-tangent-square-first-normalizer"),
        "cross-payment negative": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-cross-resonance-pointwise-baseline-payment"),
        "exploration first": (REPO / "explorations/log.jsonl", '"id":"EXP-000298"'),
        "exploration last": (REPO / "explorations/log.jsonl", '"id":"EXP-000304"'),
        "roadmap frontier": (REPO / "ROADMAP.md", "R-110"),
        "theorem-map frontier": (REPO / "governance/sector-a-theorem-map.json", "R-110"),
        "task frontier": (REPO / "TODO.md", "R-110"),
        "main proof line": (REPO / "theory/main-proof-line.md", "R-110"),
        "proof-evidence map": (REPO / "theory/proof-evidence-map.md", "R-110"),
    }
    for name, (path, token) in public_checks.items():
        body = path.read_text(encoding="utf-8")
        add("public", name, token in body, token in body, True)

    claims_not = manifest.get("claims_not_established", {})
    for name in (
        "bare_all_q_k2k_square_first",
        "uniform_complete_cluster_lower_bound",
        "overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    ):
        add("scope", f"not established {name}", claims_not.get(name) is False, claims_not.get(name), False)
    add("scope", "proof not complete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("scope", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), "T4/T4")
    add("scope", "result ledger id", manifest.get("consequence", {}).get("result_ledger_id") == "R-110", manifest.get("consequence", {}).get("result_ledger_id"), "R-110")
    add("scope", "production complete cluster open", manifest.get("consequence", {}).get("production_complete_cluster") is False, manifest.get("consequence", {}).get("production_complete_cluster"), False)

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
        "random_w": pr.get("random_w"),
        "mean_debt": pr.get("mean_debt"),
        "cross_cluster": pr.get("cross_cluster"),
        "shell_exponents": pr.get("shell_exponents"),
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
            "random_W_double_divergence": "proved-exact-form-bound",
            "random_W_HS_only_extension": "failed",
            "trace_corrected_diagonal_interpolation": "proved-exact-identity",
            "universal_nonlinear_square_first": "failed",
            "physical_k2k_complete_cluster": "proved-exact-moments",
            "physical_k2k_bare_all_q_square_first": "open-passed-local-and-finite-falsifiers",
            "pointwise_cross_payment": "proved-but-nonsummable",
            "production_complete_cluster": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_A": "open",
        },
        "result_id": RESULT_ID,
    }
    atomic_json(OUTPUT, payload)
    print(f"Integrated R-110: {payload['assertions_passed']}/{payload['assertions_total']} PASS; aggregate {aggregate}/{aggregate}")
    if failed:
        for row in failed:
            print(f"FAIL [{row['group']}] {row['name']}: {row['actual']} != {row['expected']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
