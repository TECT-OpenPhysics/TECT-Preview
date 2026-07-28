#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-107 package."""

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
RESULT_ID = "A13-CLASSII-COHERENT-OUTPUT-CLUSTER-PREDICTABLE-BASELINE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_coherent_output_cluster_predictable_baseline_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_coherent_output_cluster_predictable_baseline_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-coherent-output-cluster-predictable-baseline-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-coherent-output-cluster-predictable-baseline-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-coherent-output-cluster-predictable-baseline-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-coherent-output-cluster-predictable-baseline-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-coherent-output-cluster-predictable-baseline-boundary/result.json"

PRIMARY_ASSERTION_ORACLE = 80
INDEPENDENT_ASSERTION_ORACLE = 139
INTEGRATED_ASSERTION_ORACLE: int | None = 239

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r077": f"claims/{CLAIM}/classii_causal_packet_payload_resonance_manifest.json",
    "r079": f"claims/{CLAIM}/classii_full_safe_packet_frame_current_doob_manifest.json",
    "r082": f"claims/{CLAIM}/classii_stopped_current_far_complete_current_near_reduction_manifest.json",
    "r093": f"claims/{CLAIM}/classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r097": f"claims/{CLAIM}/classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
    "r100": f"claims/{CLAIM}/classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r106": f"claims/{CLAIM}/classii_gibbs_endpoint_production_merge_boundary_manifest.json",
}

PRIMARY_LOAD_BEARING = (
    "forward entropy production",
    "reverse entropy production",
    "conditional M2 equals M1",
    "adaptive row normalization defect positive",
    "likelihood centered form",
    "whole-output det2 identity",
    "whole-output Hilbert-Schmidt bound",
    "combined determinant",
    "independent normalizer slack positive",
    "repeated-row slack grows linearly",
    "zero output packet negative",
    "cluster expectation cancels",
    "centered base action normal form",
    "predictable covariance mass",
    "complete companion cancellation",
    "conditional KL decomposition",
    "carrier bridge diverges at diagonal",
    "convexified Gaussian divergence identity",
    "linear-flow change of variables",
)

INDEPENDENT_LOAD_BEARING = (
    "two-atom forward entropy production",
    "two-atom reverse entropy production",
    "independent mean M1",
    "adaptive row mean exceeds one",
    "hand combined determinant",
    "hand independent normalizer ratio",
    "hand repeated-row ratio",
    "finite-tree predictable action identity",
    "finite-tree nonvacuous innovation",
    "independent covariance mass",
    "independent same-root random heat guard",
    "separated companion growth",
    "signed companion decay",
    "independent quarter bridge",
    "carrier diagonal divergence sequence",
    "independent convexified identity 0",
    "independent flow identity 3",
)

NOTE_TOKENS = (
    "R-107",
    "evidence-anchor: theorem-2.1-endpoint-entropy-production",
    "evidence-anchor: theorem-3.1-backward-resolvent-likelihood-martingale",
    "evidence-anchor: proposition-3.2-progressive-future-row-normalization-defect",
    "evidence-anchor: proposition-4.1-coherent-output-trace-allocation",
    "evidence-anchor: theorem-5.1-frozen-whole-output-det2",
    "evidence-anchor: proposition-6.1-one-pair-output-cluster",
    "evidence-anchor: proposition-8.1-coherent-same-root-residual",
    "evidence-anchor: target-13.1-adapted-complete-cluster-matrix-carleson",
    r"\mathfrak R_{\rm coh}",
    r"-{d\over2}\log t",
    "single output frequency is not a signed atom",
    "rowwise predictability does not license",
    "NELSON AND SECTOR A OPEN",
)

EXPLORATIONS = {
    "EXP-000276": "advanced",
    "EXP-000277": "advanced",
    "EXP-000278": "failed",
    "EXP-000279": "failed",
    "EXP-000280": "advanced",
    "EXP-000281": "failed",
    "EXP-000282": "failed",
    "EXP-000283": "inconclusive",
    "EXP-000284": "failed",
}

NEGATIVE_IDS = (
    "NG-2026-07-28-A13-PREDICTABLE-MULTIROW-BACKWARD-RESOLVENT",
    "NG-2026-07-28-A13-SINGLE-OUTPUT-FREQUENCY-PACKET",
    "NG-2026-07-28-A13-INDEPENDENT-OUTPUT-DETERMINANT-NORMALIZATION",
    "NG-2026-07-28-A13-ADAPTED-SECOND-JET-TERMSEPARATION",
    "NG-2026-07-28-A13-PURE-CARRIER-KL-DIAGONAL-BRIDGE",
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
    for label, script, result_path, expected_count, expected_schema in (
        ("primary", PRIMARY, PRIMARY_RESULT, PRIMARY_ASSERTION_ORACLE, "tect/a13-coherent-output-cluster-predictable-baseline-boundary-primary/1.0"),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT, INDEPENDENT_ASSERTION_ORACLE, "tect/a13-coherent-output-cluster-predictable-baseline-boundary-independent/1.0"),
    ):
        result_path.unlink(missing_ok=True)
        process = subprocess.run([sys.executable, str(script), "--output", str(result_path)], cwd=REPO, text=True, capture_output=True)
        add("execution", f"{label} exit zero", process.returncode == 0, process.returncode, 0)
        add("execution", f"{label} emitted result", result_path.exists(), result_path.exists(), True)
        if not result_path.exists():
            continue
        record = load_json(result_path)
        records[label] = record
        add("execution", f"{label} schema", record.get("schema") == expected_schema, record.get("schema"), expected_schema)
        add("execution", f"{label} pass contract", result_passes(record), record.get("status"), "PASS")
        add("execution", f"{label} assertion oracle", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        add("execution", f"{label} results hash", record.get("results_sha256") == canonical_results_hash(record), record.get("results_sha256"), canonical_results_hash(record))

    if set(records) == {"primary", "independent"}:
        add("independence", "child result hashes differ", records["primary"].get("results_sha256") != records["independent"].get("results_sha256"), records["primary"].get("results_sha256"), "different")
        add("independence", "primary load-bearing assertions", set(PRIMARY_LOAD_BEARING) <= assertion_names(records["primary"]), sorted(set(PRIMARY_LOAD_BEARING) - assertion_names(records["primary"])), [])
        add("independence", "independent load-bearing assertions", set(INDEPENDENT_LOAD_BEARING) <= assertion_names(records["independent"]), sorted(set(INDEPENDENT_LOAD_BEARING) - assertion_names(records["independent"])), [])
        for label in ("primary", "independent"):
            verdicts = records[label].get("route_verdicts", {})
            add("boundary", f"{label} jointly frozen branch closed", str(verdicts.get("jointly_frozen_whole_output", "")).startswith("closed"), verdicts.get("jointly_frozen_whole_output"), "closed-*")
            add("boundary", f"{label} progressive future-row global resolvent failed", str(verdicts.get("progressive_future_row_backward_resolvent", "")).startswith("failed"), verdicts.get("progressive_future_row_backward_resolvent"), "failed-*")
        for key in ("adapted_complete_cluster_matrix_carleson", "overlap_src", "nelson", "sector_a"):
            add("firewall", f"primary {key} stays open", records["primary"].get("route_verdicts", {}).get(key) == "open", records["primary"].get("route_verdicts", {}).get(key), "open")
            add("firewall", f"independent {key} stays open", records["independent"].get("route_verdicts", {}).get(key) == "open", records["independent"].get("route_verdicts", {}).get(key), "open")
        for key in ("q", "source_budget", "sextic_budget", "scalar_total_determinant", "scalar_tail_determinant", "matrix_combined_determinant"):
            add("crosscheck", f"child derived agreement {key}", records["primary"].get("derived", {}).get(key) == records["independent"].get("derived", {}).get(key), records["primary"].get("derived", {}).get(key), records["independent"].get("derived", {}).get(key))

    independent_imports = imported_roots(INDEPENDENT)
    add("independence", "independent does not import primary", "a13_classii_coherent_output_cluster_predictable_baseline_boundary" not in INDEPENDENT.read_text(encoding="utf-8"), sorted(independent_imports), "no primary import")
    add("independence", "independent avoids scientific stacks", not ({"sympy", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "no sympy/numpy/scipy")
    add("independence", "source files are distinct", digest(PRIMARY) != digest(INDEPENDENT), digest(PRIMARY), "different")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    add("note", "note exists", NOTE.exists(), NOTE.exists(), True)
    for token in NOTE_TOKENS:
        add("note", f"note token {token[:42]}", token in note_text, token in note_text, True)
    add("note", "note has no unresolved TBD", "TBD" not in note_text, "TBD" in note_text, False)
    add("note", "note states target not theorem", "are targets, not theorems" in note_text, "are targets, not theorems" in note_text, True)

    add("pdf", "PDF exists", PDF.exists(), PDF.exists(), True)
    if PDF.exists():
        reader = PdfReader(str(PDF))
        pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        add("pdf", "PDF page count positive", len(reader.pages) > 0, len(reader.pages), ">0")
        add("pdf", "PDF has no form fields", not (reader.get_fields() or {}), len(reader.get_fields() or {}), 0)
        add("pdf", "PDF extracts result id", RESULT_ID in pdf_text, RESULT_ID in pdf_text, True)
        add("pdf", "PDF extracts no-overclaim", "NELSON AND SECTOR A OPEN" in pdf_text, "NELSON AND SECTOR A OPEN" in pdf_text, True)
        add("pdf", "PDF extracts cluster target", "contraction-closed cluster" in pdf_text, "contraction-closed cluster" in pdf_text, True)

    manifest = load_json(MANIFEST) if MANIFEST.exists() else {}
    add("manifest", "manifest exists", MANIFEST.exists(), MANIFEST.exists(), True)
    add("manifest", "manifest result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
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
    if INTEGRATED_ASSERTION_ORACLE is not None:
        add("contract", "manifest integrated assertion contract", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
        expected_aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE
        add("contract", "manifest aggregate assertion contract", contract.get("aggregate_assertions") == expected_aggregate, contract.get("aggregate_assertions"), expected_aggregate)
    add("contract", "manifest reproduction command", contract.get("command") == str(sys.executable) + " " + PRIMARY.relative_to(REPO).as_posix().replace("a13_classii_coherent_output_cluster_predictable_baseline_boundary.py", "a13_classii_coherent_output_cluster_predictable_baseline_boundary_verify.py"), contract.get("command"), "current venv verifier command")
    add("contract", "manifest adaptive negative listed", "NG-2026-07-28-A13-PREDICTABLE-MULTIROW-BACKWARD-RESOLVENT" in manifest.get("negative_results", []), manifest.get("negative_results", []), "contains adaptive multirow no-go")

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        add("negative", f"registered {negative_id}", negative_id in registry, negative_id in registry, True)
    exploration_records = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_map = {str(record.get("id")): record for record in exploration_records}
    for exploration_id, verdict in EXPLORATIONS.items():
        record = exploration_map.get(exploration_id, {})
        add("exploration", f"{exploration_id} exists", bool(record), bool(record), True)
        add("exploration", f"{exploration_id} verdict", record.get("verdict") == verdict, record.get("verdict"), verdict)
        add("exploration", f"{exploration_id} task", record.get("task_id") == "T-050", record.get("task_id"), "T-050")

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
            current_reference = "R-107" in content
            reference_name = f"{label} references R-107"
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
        add("scope", f"{label} states jointly frozen boundary", "jointly frozen" in content.lower(), "jointly frozen" in content.lower(), True)
        add("scope", f"{label} rejects rowwise predictability", "rowwise predictability" in content.lower(), "rowwise predictability" in content.lower(), True)

    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    for token in (
        "a13_classii_coherent_output_cluster_predictable_baseline_boundary_verify.py",
        "primary `80/80`",
        "independent `139/139`",
        "integrated `239/239`",
        "aggregate `458/458`",
    ):
        add("reproduction", f"claim current reproduction token {token}", token in claim_text, token in claim_text, True)

    consequence = manifest.get("consequence", {})
    for key in ("adapted_complete_cluster_bound", "full_overlap_src", "nelson", "sector_a_closure"):
        add("firewall", f"manifest {key} false", consequence.get(key) is False, consequence.get(key), False)
    for key in ("overlap_src", "nelson", "cutoff_removal", "floor_removal", "interacting_measure", "sector_a_closure", "tier_promotion"):
        add("firewall", f"claims-not-established {key}", manifest.get("claims_not_established", {}).get(key) is False, manifest.get("claims_not_established", {}).get(key), False)
    add("firewall", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("firewall", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), ("T4", "T4"))
    add("firewall", "no-overclaim names open target", "adapted complete-cluster" in str(manifest.get("no_overclaim", "")), manifest.get("no_overclaim"), "mentions adapted complete-cluster")

    if INTEGRATED_ASSERTION_ORACLE is not None:
        add("contract", "integrated assertion oracle", len(rows) + 1 == INTEGRATED_ASSERTION_ORACLE, len(rows) + 1, INTEGRATED_ASSERTION_ORACLE)

    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
    payload: dict[str, Any] = {
        "schema": "tect/a13-coherent-output-cluster-predictable-baseline-boundary-integrated/1.0",
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
            "jointly_frozen_whole_output": "closed",
            "one_step_predictable_whole_output": "closed",
            "progressive_future_row_backward_resolvent": "failed",
            "single_output_frequency": "failed",
            "independent_output_normalizers": "failed",
            "adapted_second_jet_separation": "failed",
            "pure_carrier_kl_bridge": "failed",
            "convexified_divergence_flow": "parked",
            "adapted_complete_cluster_matrix_carleson": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    if not count_only:
        atomic_json(OUTPUT, payload)
    if failed:
        for row in failed[:25]:
            print(f"FAIL {row['group']}: {row['name']}: {row['actual']} != {row['expected']}")
    child_passed = sum(int(records.get(label, {}).get("assertions_passed", 0)) for label in ("primary", "independent"))
    aggregate_passed = child_passed + int(payload["assertions_passed"])
    print(f"Integrated R-107: {payload['assertions_passed']}/{payload['assertions_total']} {'PASS' if not failed else 'FAIL'}; aggregate {aggregate_passed}/{aggregate}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
