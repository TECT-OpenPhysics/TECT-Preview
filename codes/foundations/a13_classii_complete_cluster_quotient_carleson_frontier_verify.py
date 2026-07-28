#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-108 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-COMPLETE-CLUSTER-QUOTIENT-CARLESON-FRONTIER"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_complete_cluster_quotient_carleson_frontier.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_complete_cluster_quotient_carleson_frontier_independent.py"
NOTE = CLAIM_DIR / "notes/classii-complete-cluster-quotient-carleson-frontier-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-complete-cluster-quotient-carleson-frontier-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_complete_cluster_quotient_carleson_frontier_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-complete-cluster-quotient-carleson-frontier/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-complete-cluster-quotient-carleson-frontier/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-complete-cluster-quotient-carleson-frontier/result.json"

PRIMARY_ASSERTION_ORACLE = 66
INDEPENDENT_ASSERTION_ORACLE = 90
INTEGRATED_ASSERTION_ORACLE = 230

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r085": f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
    "r087": f"claims/{CLAIM}/classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
    "r088": f"claims/{CLAIM}/classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r107": f"claims/{CLAIM}/classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
}

PRIMARY_LOAD_BEARING = (
    "historical Schur constant",
    "direct Schur constant",
    "complete endpoint subdivision invariant",
    "complete conditional endpoint identity",
    "complete endpoint optimized formula",
    "complete cluster mean covariance identity",
    "average before square leading deficit",
    "realized square has leading room",
    "averaged covariance sextic threshold",
    "explicit projected tangent formula",
    "rank one square quartic growth",
    "q scaled source reserve",
)

INDEPENDENT_LOAD_BEARING = (
    "independent historical Schur constant",
    "independent direct Schur constant",
    "independent F65 sign change",
    "independent owner defects cancel",
    "independent complete conditional endpoint identity",
    "independent optimized endpoint formula",
    "independent complete cluster identity",
    "independent square order strict",
    "independent finite average-first failure",
    "independent finite square-first room",
    "independent large tangent square",
    "independent signed second jet 2",
)

NOTE_TOKENS = (
    "R-108",
    "evidence-anchor: proposition-3.1-historical-f65-versus-complete-endpoint",
    "evidence-anchor: theorem-4.1-complete-endpoint-conditional-mean-covariance",
    "evidence-anchor: corollary-4.2-exact-cm-minimization",
    "evidence-anchor: theorem-5.1-complete-cluster-signed-normal-form",
    "evidence-anchor: proposition-6.1-square-before-average",
    "evidence-anchor: proposition-7.1-absolute-future-feedback-carleson-nogo",
    "TARGET, NOT THEOREM",
    "average-before-square",
    "cutoff, temporally faithful chart, admissible control",
    "NELSON AND SECTOR A OPEN",
)

EXPLORATIONS = {
    "EXP-000285": "advanced",
    "EXP-000286": "failed",
    "EXP-000287": "advanced",
    "EXP-000288": "failed",
    "EXP-000289": "failed",
    "EXP-000290": "advanced",
}

NEGATIVE_IDS = (
    "NG-2026-07-28-A13-RATIONAL-TAYLOR-OWNER-SUBDIVISION",
    "NG-2026-07-28-A13-AVERAGED-COVARIANCE-BEFORE-HS-SQUARE",
    "NG-2026-07-28-A13-ABSOLUTE-FUTURE-FEEDBACK-CARTAN-CARLESON",
    "NG-2026-07-28-A13-ADAPTED-SECOND-JET-TERMSEPARATION",
)


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_results_hash(record: dict[str, Any]) -> str:
    encoded = json.dumps(record.get("results", {}), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_version(path: Path) -> str | None:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return None if match is None else match.group(1)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def assertion_names(record: dict[str, Any]) -> set[str]:
    names = record.get("assertion_names", [])
    return {str(name) for name in names} if isinstance(names, list) else set()


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    names = record.get("assertion_names")
    return (
        record.get("status") == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and record.get("assertions_failed") == 0
        and isinstance(names, list)
        and len(names) == total
        and len(set(names)) == total
    )


def main() -> int:
    count_only = "--count-only" in sys.argv
    count_workspace = tempfile.TemporaryDirectory(prefix="tect-r108-count-") if count_only else None
    rows: list[dict[str, Any]] = []

    def add(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    records: dict[str, dict[str, Any]] = {}
    executed_results: dict[str, Path] = {}
    for label, script, result_path, expected_count, expected_schema in (
        ("primary", PRIMARY, PRIMARY_RESULT, PRIMARY_ASSERTION_ORACLE, "tect/a13-complete-cluster-quotient-carleson-frontier-primary/1.0"),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT, INDEPENDENT_ASSERTION_ORACLE, "tect/a13-complete-cluster-quotient-carleson-frontier-independent/1.0"),
    ):
        executed_result = (
            Path(count_workspace.name) / f"{label}.json"
            if count_workspace is not None
            else result_path
        )
        executed_results[label] = executed_result
        executed_result.unlink(missing_ok=True)
        process = subprocess.run([sys.executable, str(script), "--output", str(executed_result)], cwd=REPO, text=True, capture_output=True)
        add("execution", f"{label} exit zero", process.returncode == 0, process.returncode, 0)
        add("execution", f"{label} emitted result", executed_result.exists(), executed_result.exists(), True)
        if not executed_result.exists():
            continue
        record = load_json(executed_result)
        records[label] = record
        add("execution", f"{label} schema", record.get("schema") == expected_schema, record.get("schema"), expected_schema)
        add("execution", f"{label} pass contract", result_passes(record), record.get("status"), "PASS")
        add("execution", f"{label} assertion oracle", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add("execution", f"{label} results hash", record.get("results_sha256") == canonical_results_hash(record), record.get("results_sha256"), canonical_results_hash(record))

    if set(records) == {"primary", "independent"}:
        add("independence", "child result hashes differ", records["primary"].get("results_sha256") != records["independent"].get("results_sha256"), records["primary"].get("results_sha256"), "different")
        add("independence", "primary load-bearing assertions", set(PRIMARY_LOAD_BEARING) <= assertion_names(records["primary"]), sorted(set(PRIMARY_LOAD_BEARING) - assertion_names(records["primary"])), [])
        add("independence", "independent load-bearing assertions", set(INDEPENDENT_LOAD_BEARING) <= assertion_names(records["independent"]), sorted(set(INDEPENDENT_LOAD_BEARING) - assertion_names(records["independent"])), [])
        for key in ("uniform_complete_cluster_lower_bound", "overlap_src", "nelson", "sector_a"):
            add("firewall", f"primary {key} stays open", records["primary"].get("route_verdicts", {}).get(key) == "open", records["primary"].get("route_verdicts", {}).get(key), "open")
            add("firewall", f"independent {key} stays open", records["independent"].get("route_verdicts", {}).get(key) == "open", records["independent"].get("route_verdicts", {}).get(key), "open")
        for key in ("q", "source_budget", "sextic_budget", "q_eta_star", "q_zeta_star", "one_chart_F_6_5", "split_F_6_5", "complete_endpoint"):
            add("crosscheck", f"child derived agreement {key}", records["primary"].get("derived", {}).get(key) == records["independent"].get("derived", {}).get(key), records["primary"].get("derived", {}).get(key), records["independent"].get("derived", {}).get(key))

    independent_imports = imported_roots(INDEPENDENT)
    add("independence", "independent does not import primary", "a13_classii_complete_cluster_quotient_carleson_frontier" not in INDEPENDENT.read_text(encoding="utf-8"), sorted(independent_imports), "no primary import")
    add("independence", "independent avoids scientific stacks", not ({"sympy", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "no sympy/numpy/scipy")
    add("independence", "source files are distinct", digest(PRIMARY) != digest(INDEPENDENT), digest(PRIMARY), "different")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    add("note", "note exists", NOTE.exists(), NOTE.exists(), True)
    for token in NOTE_TOKENS:
        add("note", f"note token {token[:44]}", token in note_text, token in note_text, True)
    add("note", "note has no unresolved TBD", "TBD" not in note_text, "TBD" in note_text, False)
    add("note", "note states identities are not bounds", "It is an identity, not positivity" in note_text, "It is an identity, not positivity" in note_text, True)

    add("pdf", "PDF exists", PDF.exists(), PDF.exists(), True)
    if PDF.exists():
        reader = PdfReader(str(PDF))
        pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        add("pdf", "PDF page count positive", len(reader.pages) > 0, len(reader.pages), ">0")
        add("pdf", "PDF has no form fields", not (reader.get_fields() or {}), len(reader.get_fields() or {}), 0)
        add("pdf", "PDF extracts result id", RESULT_ID in pdf_text, RESULT_ID in pdf_text, True)
        add("pdf", "PDF extracts no-overclaim", "NELSON AND SECTOR A OPEN" in pdf_text, "NELSON AND SECTOR A OPEN" in pdf_text, True)
        add("pdf", "PDF extracts square order", "Square the realized cluster covariance before averaging" in pdf_text, "Square the realized cluster covariance before averaging" in pdf_text, True)

    manifest = load_json(MANIFEST) if MANIFEST.exists() else {}
    add("manifest", "manifest exists", MANIFEST.exists(), MANIFEST.exists(), True)
    add("manifest", "manifest schema", manifest.get("schema") == "tect/a13-complete-cluster-quotient-carleson-frontier/1.0", manifest.get("schema"), "tect/a13-complete-cluster-quotient-carleson-frontier/1.0")
    add("manifest", "manifest package version", manifest.get("package_version") == __version__, manifest.get("package_version"), __version__)
    add("manifest", "manifest claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "manifest result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "manifest status", manifest.get("status") == "T4 ANALYTIC/EXACT/EXECUTED SYNTHESIS AND BOUNDARY; UNIFORM COMPLETE-CLUSTER LOWER BOUND, OVERLAP_SRC, NELSON, AND SECTOR A OPEN", manifest.get("status"), "T4 ANALYTIC/EXACT/EXECUTED SYNTHESIS AND BOUNDARY; UNIFORM COMPLETE-CLUSTER LOWER BOUND, OVERLAP_SRC, NELSON, AND SECTOR A OPEN")
    for label, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve()), ("proof_note", NOTE)):
        source = manifest.get("sources", {}).get(label, {})
        add("manifest", f"{label} path", REPO / str(source.get("path", "")) == path, source.get("path"), path.relative_to(REPO).as_posix())
        add("manifest", f"{label} hash", source.get("sha256") == digest(path), source.get("sha256"), digest(path))
        if label != "proof_note":
            add("manifest", f"{label} version", source.get("version") == source_version(path), source.get("version"), source_version(path))
    if PDF.exists():
        reader = PdfReader(str(PDF))
        proof_pdf = manifest.get("proof_pdf", {})
        add("manifest", "PDF hash", proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF))
        add("manifest", "PDF size", proof_pdf.get("size_bytes") == PDF.stat().st_size, proof_pdf.get("size_bytes"), PDF.stat().st_size)
        add("manifest", "PDF pages", proof_pdf.get("pages") == len(reader.pages), proof_pdf.get("pages"), len(reader.pages))
        add("manifest", "PDF form check", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
        add("manifest", "PDF overfull zero", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
        add("manifest", "PDF visual QA", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    for label, relative in AUTHORITY_MANIFESTS.items():
        authority_path = REPO / relative
        pinned = manifest.get("authority", {}).get(label, {})
        add("authority", f"{label} manifest exists", authority_path.exists(), authority_path.exists(), True)
        add("authority", f"{label} manifest path", pinned.get("manifest", {}).get("path") == relative, pinned.get("manifest", {}).get("path"), relative)
        add("authority", f"{label} manifest hash", pinned.get("manifest", {}).get("sha256") == digest(authority_path), pinned.get("manifest", {}).get("sha256"), digest(authority_path))
        authority_manifest = load_json(authority_path)
        result_relative = authority_manifest.get("run_contract", {}).get("integrated_output")
        result_path = REPO / str(result_relative)
        add("authority", f"{label} result exists", result_path.exists(), result_path.exists(), True)
        add("authority", f"{label} result path", pinned.get("result", {}).get("path") == result_relative, pinned.get("result", {}).get("path"), result_relative)
        add("authority", f"{label} result hash", pinned.get("result", {}).get("sha256") == digest(result_path), pinned.get("result", {}).get("sha256"), digest(result_path))

    contract = manifest.get("run_contract", {})
    add("contract", "primary output path", contract.get("primary_output") == PRIMARY_RESULT.relative_to(REPO).as_posix(), contract.get("primary_output"), PRIMARY_RESULT.relative_to(REPO).as_posix())
    add("contract", "independent output path", contract.get("independent_output") == INDEPENDENT_RESULT.relative_to(REPO).as_posix(), contract.get("independent_output"), INDEPENDENT_RESULT.relative_to(REPO).as_posix())
    add("contract", "integrated output path", contract.get("integrated_output") == OUTPUT.relative_to(REPO).as_posix(), contract.get("integrated_output"), OUTPUT.relative_to(REPO).as_posix())
    add("contract", "primary assertion contract", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertion contract", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary schema contract", contract.get("primary_schema") == "tect/a13-complete-cluster-quotient-carleson-frontier-primary/1.0", contract.get("primary_schema"), "tect/a13-complete-cluster-quotient-carleson-frontier-primary/1.0")
    add("contract", "independent schema contract", contract.get("independent_schema") == "tect/a13-complete-cluster-quotient-carleson-frontier-independent/1.0", contract.get("independent_schema"), "tect/a13-complete-cluster-quotient-carleson-frontier-independent/1.0")
    add("contract", "integrated schema contract", contract.get("integrated_schema") == "tect/a13-complete-cluster-quotient-carleson-frontier-integrated/1.0", contract.get("integrated_schema"), "tect/a13-complete-cluster-quotient-carleson-frontier-integrated/1.0")
    if INTEGRATED_ASSERTION_ORACLE is not None:
        add("contract", "manifest integrated assertion contract", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
        expected_aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE
        add("contract", "manifest aggregate assertion contract", contract.get("aggregate_assertions") == expected_aggregate, contract.get("aggregate_assertions"), expected_aggregate)
    expected_command = str(sys.executable) + " " + Path(__file__).resolve().relative_to(REPO).as_posix()
    add("contract", "manifest reproduction command", contract.get("command") == expected_command, contract.get("command"), expected_command)
    for label in ("primary", "independent"):
        pinned_result = manifest.get("child_results", {}).get(label, {})
        expected_path = (PRIMARY_RESULT if label == "primary" else INDEPENDENT_RESULT).relative_to(REPO).as_posix()
        add("manifest", f"{label} child result path", pinned_result.get("path") == expected_path, pinned_result.get("path"), expected_path)
        if label in executed_results and executed_results[label].exists():
            add("manifest", f"{label} child result hash", pinned_result.get("sha256") == digest(executed_results[label]), pinned_result.get("sha256"), digest(executed_results[label]))

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        add("negative", f"registered {negative_id}", negative_id in registry, negative_id in registry, True)
    add("manifest", "manifest negative result set", set(manifest.get("negative_results", [])) == set(NEGATIVE_IDS), sorted(manifest.get("negative_results", [])), sorted(NEGATIVE_IDS))
    exploration_records = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_map = {str(record.get("id")): record for record in exploration_records}
    for exploration_id, verdict in EXPLORATIONS.items():
        record = exploration_map.get(exploration_id, {})
        add("exploration", f"{exploration_id} exists", bool(record), bool(record), True)
        add("exploration", f"{exploration_id} verdict", record.get("verdict") == verdict, record.get("verdict"), verdict)
        add("exploration", f"{exploration_id} task", record.get("task_id") == "T-050", record.get("task_id"), "T-050")
    add("manifest", "manifest exploration set", set(manifest.get("explorations", [])) == set(EXPLORATIONS), sorted(manifest.get("explorations", [])), sorted(EXPLORATIONS))

    public_checks = {
        "claim card": CLAIM_DIR / "claim.md",
        "status": CLAIM_DIR / "status.json",
        "result ledger": REPO / "RESULTS-LEDGER.md",
        "roadmap": REPO / "ROADMAP.md",
        "todo": REPO / "todo/todo.json",
        "sector map": REPO / "governance/sector-a-theorem-map.json",
        "generated claims": REPO / "CLAIMS.md",
        "lineage narrative": CLAIM_DIR / "lineage-narrative.md",
        "gates": REPO / "claims/GATES.md",
        "main proof line": REPO / "theory/main-proof-line.md",
        "sector foundation": REPO / "theory/sector-A-foundation/README.md",
        "changelog": REPO / "changelog/log.jsonl",
        "proof map": REPO / "theory/proof-evidence-map.md",
    }
    for label, path in public_checks.items():
        content = path.read_text(encoding="utf-8")
        if label == "generated claims":
            current_reference = CLAIM in content
            reference_name = f"{label} references active A13 card"
        else:
            current_reference = "R-108" in content
            reference_name = f"{label} references R-108"
        add("public", reference_name, current_reference, current_reference, True)
        add("public", f"{label} keeps Sector A open", "Sector A" in content and "open" in content.lower(), "Sector A" in content, True)

    narrowed_surfaces = {
        "proof note": NOTE,
        "claim card": CLAIM_DIR / "claim.md",
        "status": CLAIM_DIR / "status.json",
        "result ledger": REPO / "RESULTS-LEDGER.md",
        "roadmap": REPO / "ROADMAP.md",
        "todo": REPO / "todo/todo.json",
        "sector map": REPO / "governance/sector-a-theorem-map.json",
    }
    for label, path in narrowed_surfaces.items():
        content = path.read_text(encoding="utf-8")
        add("scope", f"{label} names quotient-safe endpoint", "quotient" in content.lower() and "complete endpoint" in content.lower(), content.lower().count("complete endpoint"), ">0")
        add("scope", f"{label} names square-before-average", "square-before-average" in content.lower(), "square-before-average" in content.lower(), True)
        add("scope", f"{label} keeps uniform cluster bound open", "uniform" in content.lower() and "open" in content.lower(), "uniform" in content.lower(), True)

    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    for token in (
        "a13_classii_complete_cluster_quotient_carleson_frontier_verify.py",
        "primary `66/66`",
        "independent `90/90`",
    ):
        add("reproduction", f"claim current reproduction token {token}", token in claim_text, token in claim_text, True)

    consequence = manifest.get("consequence", {})
    for key in ("uniform_complete_cluster_lower_bound", "full_overlap_src", "nelson", "sector_a_closure"):
        add("firewall", f"manifest {key} false", consequence.get(key) is False, consequence.get(key), False)
    for key in ("overlap_src", "nelson", "cutoff_removal", "floor_removal", "interacting_measure", "sector_a_closure", "tier_promotion"):
        add("firewall", f"claims-not-established {key}", manifest.get("claims_not_established", {}).get(key) is False, manifest.get("claims_not_established", {}).get(key), False)
    add("firewall", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("firewall", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), ("T4", "T4"))
    add("firewall", "no-overclaim names identities not bounds", "identities" in str(manifest.get("no_overclaim", "")) and "lower bounds" in str(manifest.get("no_overclaim", "")), manifest.get("no_overclaim"), "identities are not lower bounds")

    add("contract", "integrated assertion names unique", len({str(row["name"]) for row in rows}) == len(rows), len({str(row["name"]) for row in rows}), len(rows))

    if INTEGRATED_ASSERTION_ORACLE is not None:
        add("contract", "integrated assertion oracle", len(rows) + 1 == INTEGRATED_ASSERTION_ORACLE, len(rows) + 1, INTEGRATED_ASSERTION_ORACLE)

    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
    payload: dict[str, Any] = {
        "schema": "tect/a13-complete-cluster-quotient-carleson-frontier-integrated/1.0",
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": integrated_total,
        "assertions_passed": integrated_total - len(failed),
        "assertions_failed": len(failed),
        "assertions": rows,
        "assertion_names": [str(row["name"]) for row in rows],
        "aggregate_assertions": aggregate,
        "child_assertions": {"primary": PRIMARY_ASSERTION_ORACLE, "independent": INDEPENDENT_ASSERTION_ORACLE},
        "source_hashes": {"primary": digest(PRIMARY), "independent": digest(INDEPENDENT), "verifier": digest(Path(__file__).resolve())},
        "route_verdicts": {
            "historical_R085_weighted_bridge": "superseded-and-unproved",
            "direct_R088_unweighted_bridge": "open",
            "historical_F_6_5_progressive_owner": "failed",
            "complete_endpoint_conditional_identity": "advanced",
            "complete_cluster_mean_covariance_identity": "advanced",
            "average_covariance_before_hs_square": "failed",
            "absolute_future_feedback_matrix_carleson": "failed",
            "realized_cluster_square_then_average": "viable-not-proved",
            "uniform_complete_cluster_lower_bound": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    if not count_only:
        atomic_json(OUTPUT, payload)
    if failed:
        for row in failed[:30]:
            print(f"FAIL {row['group']}: {row['name']}: {row['actual']} != {row['expected']}")
    child_passed = sum(int(records.get(label, {}).get("assertions_passed", 0)) for label in ("primary", "independent"))
    aggregate_passed = child_passed + int(payload["assertions_passed"])
    print(f"Integrated R-108: {payload['assertions_passed']}/{payload['assertions_total']} {'PASS' if not failed else 'FAIL'}; aggregate {aggregate_passed}/{aggregate}")
    if count_workspace is not None:
        count_workspace.cleanup()
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
