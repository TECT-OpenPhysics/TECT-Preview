#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-109 package."""

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
RESULT_ID = "A13-CLASSII-SQUARE-FIRST-PAIR-SCORE-TRANSFER-FILTRATION-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_square_first_pair_score_transfer_filtration_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_square_first_pair_score_transfer_filtration_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-square-first-pair-score-transfer-filtration-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-square-first-pair-score-transfer-filtration-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_square_first_pair_score_transfer_filtration_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-square-first-pair-score-transfer-filtration-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-square-first-pair-score-transfer-filtration-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-square-first-pair-score-transfer-filtration-boundary/result.json"

PRIMARY_ASSERTION_ORACLE = 39
INDEPENDENT_ASSERTION_ORACLE = 93
INTEGRATED_ASSERTION_ORACLE = 106

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r077": f"claims/{CLAIM}/classii_causal_packet_payload_resonance_manifest.json",
    "r082": f"claims/{CLAIM}/classii_stopped_current_far_complete_current_near_reduction_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r107": f"claims/{CLAIM}/classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r108": f"claims/{CLAIM}/classii_complete_cluster_quotient_carleson_frontier_manifest.json",
}

NOTE_TOKENS = (
    "R-109",
    "evidence-anchor: theorem-2.1-conditional-floor-variance-normalizer",
    "evidence-anchor: theorem-3.1-all-amplitude-one-pair-square-first",
    "evidence-anchor: corollary-3.2-fresh-pair-supermartingale",
    "evidence-anchor: audit-4.1-realized-covariance-filtration",
    "evidence-anchor: proposition-5.1-arbitrary-selector-quartic-floor",
    "evidence-anchor: proposition-5.2-full-pair-floor-boundary",
    "evidence-anchor: theorem-6.1-complete-second-jet-score-transfer",
    "evidence-anchor: proposition-7.1-stein-second-jet-exponentiation-nogo",
    "AUDIT-2026-07-28-A13-R108-REALIZED-COVARIANCE-FILTRATION",
    "NG-2026-07-28-A13-STEIN-SECOND-JET-EXPONENTIATION",
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
    results = record.get("results")
    return hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
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
    with tempfile.TemporaryDirectory(prefix="tect-r109-child-") as directory:
        output = Path(directory) / "result.json"
        process = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
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
            "tect/a13-square-first-pair-score-transfer-filtration-boundary-primary/1.0",
        ),
        (
            "independent",
            INDEPENDENT,
            INDEPENDENT_RESULT,
            INDEPENDENT_ASSERTION_ORACLE,
            "tect/a13-square-first-pair-score-transfer-filtration-boundary-independent/1.0",
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
    pderived = primary.get("derived", {})
    iderived = independent.get("derived", {})
    add("cross", "q agreement", pderived.get("q") == iderived.get("q") == "10/9", (pderived.get("q"), iderived.get("q")), "10/9")
    add("cross", "threshold agreement", pderived.get("bennett_threshold") == iderived.get("bennett_threshold") == "1/5", (pderived.get("bennett_threshold"), iderived.get("bennett_threshold")), "1/5")
    add("cross", "small branch multiplier agreement", pderived.get("small_branch_multiplier") == iderived.get("small_branch_multiplier") == "30/7", (pderived.get("small_branch_multiplier"), iderived.get("small_branch_multiplier")), "30/7")
    add("cross", "one-pair second moment agreement", pderived.get("one_pair_variance") == "8" and iderived.get("one_pair_moments", {}).get("second") == 8, (pderived.get("one_pair_variance"), iderived.get("one_pair_moments")), "8")
    add("cross", "small-q coefficient", pderived.get("one_pair_small_q_coefficient") == "4", pderived.get("one_pair_small_q_coefficient"), "4")
    add("cross", "square-first coefficient", pderived.get("square_first_coefficient") == "5", pderived.get("square_first_coefficient"), "5")
    add("cross", "score constant agreement", pderived.get("score_transfer_q_constant") == iderived.get("score_constant") == "25/1296", (pderived.get("score_transfer_q_constant"), iderived.get("score_constant")), "25/1296")
    add("cross", "quartic shell exponent agreement", pderived.get("quartic_floor_shell_exponent") == str(iderived.get("quartic_shell_exponent")) == "-3", (pderived.get("quartic_floor_shell_exponent"), iderived.get("quartic_shell_exponent")), "-3")
    add("cross", "baseline shell exponent agreement", pderived.get("baseline_floor_shell_exponent") == str(iderived.get("baseline_shell_exponent")) == "1", (pderived.get("baseline_floor_shell_exponent"), iderived.get("baseline_shell_exponent")), "1")
    add("cross", "determinant shell exponent agreement", pderived.get("determinant_shell_exponent") == str(iderived.get("determinant_shell_exponent")) == "-1", (pderived.get("determinant_shell_exponent"), iderived.get("determinant_shell_exponent")), "-1")
    add("cross", "derivative covariance shell agreement", pderived.get("derivative_covariance_hs_shell_exponent") == str(iderived.get("derivative_covariance_hs_shell_exponent")) == "-1", (pderived.get("derivative_covariance_hs_shell_exponent"), iderived.get("derivative_covariance_hs_shell_exponent")), "-1")
    add("cross", "one-pair route closed", primary.get("route_verdicts", {}).get("one_pair_square_before_average_all_amplitudes") == "proved-conditional-fresh-pair", primary.get("route_verdicts", {}).get("one_pair_square_before_average_all_amplitudes"), "proved-conditional-fresh-pair")
    add("cross", "Stein route failed", primary.get("route_verdicts", {}).get("stein_derivative_inside_exponential") == "failed" and independent.get("route_verdicts", {}).get("Stein_exponentiation") == "fail", (primary.get("route_verdicts", {}).get("stein_derivative_inside_exponential"), independent.get("route_verdicts", {}).get("Stein_exponentiation")), "failed/fail")
    add("cross", "Sector A remains open", primary.get("route_verdicts", {}).get("sector_a") == "open" and independent.get("route_verdicts", {}).get("sector_A") == "open", (primary.get("route_verdicts", {}).get("sector_a"), independent.get("route_verdicts", {}).get("sector_A")), "open/open")

    expected_sources = manifest.get("sources", {})
    source_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": VERIFIER, "proof_note": NOTE}
    for label, path in source_paths.items():
        item = expected_sources.get(label, {})
        add("hash", f"{label} path", item.get("path") == path.relative_to(REPO).as_posix(), item.get("path"), path.relative_to(REPO).as_posix())
        add("hash", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        item = manifest.get("child_results", {}).get(label, {})
        add("hash", f"{label} result path", item.get("path") == path.relative_to(REPO).as_posix(), item.get("path"), path.relative_to(REPO).as_posix())
        add("hash", f"{label} result digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    for label, relative in AUTHORITY_MANIFESTS.items():
        authority = manifest.get("authority", {}).get(label, {})
        path = REPO / relative
        add("authority", f"{label} manifest path", authority.get("manifest", {}).get("path") == relative, authority.get("manifest", {}).get("path"), relative)
        add("authority", f"{label} manifest digest", authority.get("manifest", {}).get("sha256") == digest(path), authority.get("manifest", {}).get("sha256"), digest(path))

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"note token {token[:48]}", token in note_text, token in note_text, True)
    add("note", "note no target theorem overclaim", "full adapted production cluster" in note_text and "remain open" in note_text, "full adapted production cluster" in note_text, True)
    add("note", "note exact expected counts", "primary 39/39; independent 93/93" in note_text, "primary 39/39; independent 93/93" in note_text, True)

    reader = PdfReader(str(PDF))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    pdf_item = manifest.get("proof_pdf", {})
    add("pdf", "PDF page count", len(reader.pages) == 10, len(reader.pages), 10)
    add("pdf", "PDF manifest page count", pdf_item.get("pages") == len(reader.pages), pdf_item.get("pages"), len(reader.pages))
    add("pdf", "PDF digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))
    add("pdf", "PDF size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "PDF visual QA contract", pdf_item.get("visual_qa") == "PASS", pdf_item.get("visual_qa"), "PASS")
    add("pdf", "PDF form contract", pdf_item.get("form_check") == "PASS", pdf_item.get("form_check"), "PASS")
    add("pdf", "PDF extracted title", "pair normalizer, signed score transfer" in extracted, "pair normalizer, signed score transfer" in extracted, True)
    add("pdf", "PDF extracted theorem", "all-amplitude square-before-average normalizer" in extracted, "all-amplitude square-before-average normalizer" in extracted, True)

    contract = manifest.get("run_contract", {})
    add("contract", "primary assertion contract", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertion contract", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary schema contract", contract.get("primary_schema") == child_specs[0][4], contract.get("primary_schema"), child_specs[0][4])
    add("contract", "independent schema contract", contract.get("independent_schema") == child_specs[1][4], contract.get("independent_schema"), child_specs[1][4])
    integrated_schema = "tect/a13-square-first-pair-score-transfer-filtration-boundary-integrated/1.0"
    add("contract", "integrated schema contract", contract.get("integrated_schema") == integrated_schema, contract.get("integrated_schema"), integrated_schema)
    expected_command = str(sys.executable) + " " + VERIFIER.relative_to(REPO).as_posix()
    add("contract", "reproduction command", contract.get("command") == expected_command, contract.get("command"), expected_command)
    if INTEGRATED_ASSERTION_ORACLE is not None:
        add("contract", "manifest integrated assertion contract", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
        add("contract", "manifest aggregate assertion contract", contract.get("aggregate_assertions") == PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE, contract.get("aggregate_assertions"), PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE)

    public_checks = {
        "claim card R-109": (CLAIM_DIR / "claim.md", "R-109"),
        "status R-109": (CLAIM_DIR / "status.json", "R-109"),
        "results ledger R-109": (REPO / "RESULTS-LEDGER.md", "<a id=\"r-109\"></a>"),
        "audit registry": (REPO / "negative-results/registry.md", "audit-2026-07-28-a13-r108-realized-covariance-filtration"),
        "negative registry": (REPO / "negative-results/registry.md", "ng-2026-07-28-a13-stein-second-jet-exponentiation"),
        "exploration first": (REPO / "explorations/log.jsonl", '"id":"EXP-000291"'),
        "exploration last": (REPO / "explorations/log.jsonl", '"id":"EXP-000297"'),
        "roadmap frontier": (REPO / "ROADMAP.md", "R-109"),
        "theorem-map frontier": (REPO / "governance/sector-a-theorem-map.json", "R-109"),
        "task frontier": (REPO / "TODO.md", "R-109"),
        "main proof line": (REPO / "theory/main-proof-line.md", "R-109"),
        "proof-evidence map": (REPO / "theory/proof-evidence-map.md", "R-109"),
    }
    for name, (path, token) in public_checks.items():
        text = path.read_text(encoding="utf-8")
        add("public", name, token in text, token in text, True)

    claims_not = manifest.get("claims_not_established", {})
    for name in (
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
    add("scope", "result ledger id", manifest.get("consequence", {}).get("result_ledger_id") == "R-109", manifest.get("consequence", {}).get("result_ledger_id"), "R-109")
    add("scope", "full production open", manifest.get("consequence", {}).get("production_complete_cluster") is False, manifest.get("consequence", {}).get("production_complete_cluster"), False)

    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    if INTEGRATED_ASSERTION_ORACLE is not None and integrated_total != INTEGRATED_ASSERTION_ORACLE:
        rows.append(
            {
                "group": "contract",
                "name": "integrated source assertion oracle",
                "status": "FAIL",
                "actual": str(integrated_total),
                "expected": str(INTEGRATED_ASSERTION_ORACLE),
            }
        )
        failed = [row for row in rows if row["status"] != "PASS"]
        integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
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
        "source_hashes": {"primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "verifier": digest(VERIFIER)},
        "route_verdicts": {
            "one_pair_square_first": "proved-all-amplitudes",
            "fresh_pair_supermartingale": "proved",
            "R108_realized_covariance_filtration": "repaired",
            "pure_quartic_selector_floor": "proved-diagonal-submodel",
            "fixed_W_score_transfer": "proved-expectation-only",
            "Stein_exponentiation": "failed",
            "production_complete_cluster": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_A": "open",
        },
    }
    atomic_json(OUTPUT, payload)
    child_passed = sum(int(children[label].get("assertions_passed", 0)) for label in children)
    aggregate_passed = child_passed + int(payload["assertions_passed"])
    print(
        f"Integrated R-109: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"{'PASS' if not failed else 'FAIL'}; aggregate {aggregate_passed}/{aggregate}"
    )
    if failed:
        for row in failed[:30]:
            print(f"FAIL {row['group']}: {row['name']}: {row['actual']} != {row['expected']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
