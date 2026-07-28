#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-114 scalar package."""

from __future__ import annotations

__version__ = "1.1.0"
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
RESULT_ID = "A13-CLASSII-SCALAR-K2K-SUPPORT-TWO-MOMENT-CONE-CLOSURE"
NEGATIVE_ID = "NG-2026-07-28-A13-K2K-CUBIC-KS-PROXY-BEYOND-CONE"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_support_two_moment_cone.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_support_two_moment_cone_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-scalar-k2k-support-two-moment-cone-closure-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-scalar-k2k-support-two-moment-cone-closure-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_scalar_k2k_support_two_moment_cone_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-support-two-moment-cone/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-support-two-moment-cone/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-scalar-k2k-support-two-moment-cone/result.json"

PRIMARY_ASSERTION_ORACLE = 155
INDEPENDENT_ASSERTION_ORACLE = 133

AUTHORITY_MANIFESTS = {
    "r087": f"claims/{CLAIM}/classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r112": f"claims/{CLAIM}/classii_scalar_k2k_covariance_simplex_uniform_compact_core_manifest.json",
    "r113": f"claims/{CLAIM}/classii_scalar_k2k_effective_boundary_interval_seed_manifest.json",
}

NOTE_TOKENS = (
    "R-114",
    RESULT_ID,
    "support--two-moment",
    "3981",
    "0\\le x\\le643\\tau/200",
    "Theorem 4.1",
    "A reusable symmetric Bessel majorant",
    "Exact remaining scalar frontier",
    "Method boundary and proof roadmap",
    "b>643/200",
    "Sector A remain open",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, object]) -> None:
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
    encoded = json.dumps(record.get("results"), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    with tempfile.TemporaryDirectory(prefix="tect-r114-child-") as directory:
        output = Path(directory) / "result.json"
        process = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if process.returncode != 0:
            return {"execution_error": process.stderr or process.stdout, "returncode": process.returncode}
        record = load_json(output)
        record["returncode"] = process.returncode
        record["stdout"] = process.stdout.strip()
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
    pinned_primary = load_json(PRIMARY_RESULT)
    pinned_independent = load_json(INDEPENDENT_RESULT)

    add("manifest", "schema", manifest.get("schema") == "tect/a13-scalar-k2k-support-two-moment-cone/1.0", manifest.get("schema"), "declared schema")
    add("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "tier stays T4", manifest.get("tier_before") == "T4" and manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), ("T4", "T4"))
    add("manifest", "proof remains incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)

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
        path = REPO / relative
        item = manifest.get("authority", {}).get(label, {}).get("manifest", {})
        add("authority", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("authority", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    contract = manifest.get("run_contract", {})
    add("contract", "primary schema", contract.get("primary_schema") == pinned_primary.get("schema"), contract.get("primary_schema"), pinned_primary.get("schema"))
    add("contract", "independent schema", contract.get("independent_schema") == pinned_independent.get("schema"), contract.get("independent_schema"), pinned_independent.get("schema"))
    add("contract", "primary assertion oracle", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertion oracle", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "integrated assertion oracle", contract.get("integrated_assertions") == 140, contract.get("integrated_assertions"), 140)
    add("contract", "aggregate assertion oracle", contract.get("aggregate_assertions") == 428, contract.get("aggregate_assertions"), 428)
    add("contract", "coefficient signs", contract.get("exact_coefficient_signs_per_child") == 3981, contract.get("exact_coefficient_signs_per_child"), 3981)
    add("contract", "canonical command", contract.get("command") == r"E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/a13_classii_scalar_k2k_support_two_moment_cone_verify.py", contract.get("command"), "canonical command")

    add("pinned", "primary pinned result passes", result_passes(pinned_primary, PRIMARY_ASSERTION_ORACLE), pinned_primary.get("status"), "PASS")
    add("pinned", "independent pinned result passes", result_passes(pinned_independent, INDEPENDENT_ASSERTION_ORACLE), pinned_independent.get("status"), "PASS")

    fresh_primary = execute_child(PRIMARY)
    fresh_independent = execute_child(INDEPENDENT)
    add("execution", "primary fresh result passes", result_passes(fresh_primary, PRIMARY_ASSERTION_ORACLE), fresh_primary.get("status"), "PASS")
    add("execution", "independent fresh result passes", result_passes(fresh_independent, INDEPENDENT_ASSERTION_ORACLE), fresh_independent.get("status"), "PASS")
    add("execution", "primary pinned/fresh results", pinned_primary.get("results_sha256") == fresh_primary.get("results_sha256"), fresh_primary.get("results_sha256"), pinned_primary.get("results_sha256"))
    add("execution", "independent pinned/fresh results", pinned_independent.get("results_sha256") == fresh_independent.get("results_sha256"), fresh_independent.get("results_sha256"), pinned_independent.get("results_sha256"))

    primary_results = pinned_primary.get("results", {})
    independent_results = pinned_independent.get("results", {})
    add("agreement", "primary coefficient count", primary_results.get("exact_coefficient_signs") == 3981, primary_results.get("exact_coefficient_signs"), 3981)
    add("agreement", "independent coefficient count", independent_results.get("exact_coefficient_signs") == 3981, independent_results.get("exact_coefficient_signs"), 3981)
    add("agreement", "primary cone", primary_results.get("cone", {}).get("condition") == "tau>0 and 0<=x<=643*tau/200", primary_results.get("cone", {}).get("condition"), "declared cone")
    add("agreement", "independent cone", independent_results.get("cone") == "tau>0 and 0<=x<=643*tau/200", independent_results.get("cone"), "declared cone")
    add("agreement", "both strict", primary_results.get("cone", {}).get("strict_gap") is True and independent_results.get("strict_gap") is True, (primary_results.get("cone", {}).get("strict_gap"), independent_results.get("strict_gap")), (True, True))
    add("agreement", "both origin equality", primary_results.get("cone", {}).get("origin_equality") is True and independent_results.get("origin_equality") is True, (primary_results.get("cone", {}).get("origin_equality"), independent_results.get("origin_equality")), (True, True))

    primary_certificates = primary_results.get("bernstein_certificates", {})
    independent_certificates = independent_results.get("certificates", {})
    for label in ("I1", "I2", "I3", "I4"):
        primary_item = primary_certificates.get(label, {})
        independent_item = independent_certificates.get(label, {})
        for field_primary, field_independent in (
            ("S_coefficient_count", "S_count"),
            ("Q_coefficient_count", "Q_count"),
            ("S_minimum", "S_minimum"),
            ("Q_minimum", "Q_minimum"),
            ("S_sha256", "S_sha256"),
            ("Q_sha256", "Q_sha256"),
        ):
            add(
                "agreement",
                f"{label} {field_primary}",
                primary_item.get(field_primary) == independent_item.get(field_independent),
                primary_item.get(field_primary),
                independent_item.get(field_independent),
            )

    primary_i5 = primary_certificates.get("I5", {})
    independent_i5 = independent_certificates.get("I5", {})
    for primary_field, independent_field in (
        ("Q_coefficient_count", "Q_count"),
        ("Q_minimum", "Q_minimum"),
        ("Q_sha256", "Q_sha256"),
    ):
        add("agreement", f"I5 {primary_field}", primary_i5.get(primary_field) == independent_i5.get(independent_field), primary_i5.get(primary_field), independent_i5.get(independent_field))

    primary_i6 = primary_certificates.get("I6", {}).get("regions", {})
    independent_i6 = independent_certificates.get("I6", {}).get("regions", {})
    for label in ("Q_LOW", "S_A", "S_B", "S_C", "S_D", "Q_HIGH"):
        for field in ("coefficient_count", "minimum", "sha256"):
            add("agreement", f"I6 {label} {field}", primary_i6.get(label, {}).get(field) == independent_i6.get(label, {}).get(field), primary_i6.get(label, {}).get(field), independent_i6.get(label, {}).get(field))

    primary_witness = primary_results.get("method_boundary", {}).get("witness", {})
    independent_witness = independent_results.get("method_boundary_witness", {})
    add("agreement", "method witness exact agreement", primary_witness == independent_witness, primary_witness, independent_witness)
    add("agreement", "method witness negative Q", str(primary_witness.get("Q", "")).startswith("-"), primary_witness.get("Q"), "<0")
    add("agreement", "method witness negative S", str(primary_witness.get("S", "")).startswith("-"), primary_witness.get("S"), "<0")

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"contains {token}", token in note_text, token in note_text, True)
    add("note", "no literal qquad debris", "qquad" not in note_text.replace("\\qquad", ""), "qquad" in note_text.replace("\\qquad", ""), False)
    add("note", "devil objections", note_text.count("\\textbf{Objection:}") >= 7, note_text.count("\\textbf{Objection:}"), ">=7")

    reader = PdfReader(str(PDF))
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_item = manifest.get("proof_pdf", {})
    add("pdf", "path", pdf_item.get("path") == PDF.relative_to(REPO).as_posix(), pdf_item.get("path"), PDF.relative_to(REPO).as_posix())
    add("pdf", "digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))
    add("pdf", "page count", len(reader.pages) == pdf_item.get("pages") and len(reader.pages) >= 8, (len(reader.pages), pdf_item.get("pages")), "matching and >=8")
    add("pdf", "size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "form and visual gates", pdf_item.get("form_check") == "PASS" and pdf_item.get("overfull_hbox_count") == 0 and pdf_item.get("visual_qa") == "PASS", (pdf_item.get("form_check"), pdf_item.get("overfull_hbox_count"), pdf_item.get("visual_qa")), ("PASS", 0, "PASS"))
    add("pdf", "text extraction", "R-114" in pdf_text and "3981" in pdf_text and "Sector A remain open" in pdf_text, ("R-114" in pdf_text, "3981" in pdf_text, "Sector A remain open" in pdf_text), (True, True, True))

    status_card = load_json(CLAIM_DIR / "status.json")
    add("repository", "claim statement records R-114", "R-114" in status_card.get("statement", "") and "643/200" in status_card.get("statement", ""), status_card.get("statement", "")[:160], "R-114 cone")
    add("repository", "tier remains T4", status_card.get("tier") == "T4", status_card.get("tier"), "T4")
    add("repository", "status no-overclaim", "Sector-A closure" in status_card.get("no_overclaim", "") and "b>643/200" in status_card.get("no_overclaim", ""), status_card.get("no_overclaim", "")[-180:], "open residual and Sector A")
    results_ledger = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    explorations = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    add("repository", "result ledger entry", "### R-114 --" in results_ledger and RESULT_ID in results_ledger, "R-114" in results_ledger, True)
    add("repository", "negative registry entry", NEGATIVE_ID in negatives and "-127544381197984065" in negatives, NEGATIVE_ID in negatives, True)
    for exploration_id in manifest.get("explorations", []):
        add("repository", f"exploration {exploration_id}", f'"id":"{exploration_id}"' in explorations, exploration_id in explorations, True)

    consequence = manifest.get("consequence", {})
    required_true = (
        "support_two_moment_cone_b_le_643_over_200",
        "complete_zero_amplitude_axis",
        "r113_seed_box_subsumed",
        "independent_exact_reproduction",
        "symmetric_bessel_majorant",
    )
    required_false = (
        "mixed_all_b_scalar_k2k",
        "full_a1_embedding",
        "one_use_source_sextic_aggregation",
        "full_overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
        "target_counterexample",
    )
    for field in required_true:
        add("scope", f"{field} true", consequence.get(field) is True, consequence.get(field), True)
    for field in required_false:
        add("scope", f"{field} false", consequence.get(field) is False, consequence.get(field), False)

    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"
    results: dict[str, object] = {
        "component_assertions": {
            "primary": PRIMARY_ASSERTION_ORACLE,
            "independent": INDEPENDENT_ASSERTION_ORACLE,
            "integrated": len(rows),
            "aggregate": PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + len(rows),
        },
        "exact_coefficient_signs_per_child": 3981,
        "cone": "tau>0 and 0<=x<=643*tau/200",
        "strict_gap": True,
        "origin_equality": True,
        "remaining_scalar_region": "b>643/200 after inherited classifiers",
        "primary_results_sha256": pinned_primary.get("results_sha256"),
        "independent_results_sha256": pinned_independent.get("results_sha256"),
        "manifest_sha256": digest(MANIFEST),
    }
    payload: dict[str, object] = {
        "schema": "tect/a13-scalar-k2k-support-two-moment-cone-integrated/1.0",
        "version": __version__,
        "status": status,
        "assertions_total": len(rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in rows),
        "assertion_names": [f"{row['group']}::{row['name']}" for row in rows],
        "assertions": rows,
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "route_verdicts": {
            "support_two_moment_cone": "proved-and-independently-reproduced-through-b=643/200",
            "zero_amplitude_axis": "closed",
            "cubic_proxy_beyond_cone": "failed-at-exact-witness",
            "mixed_all_b_scalar_k2k": "open",
            "full_a1_embedding": "open",
            "one_use_source_sextic_aggregation": "open",
            "overlap_src": "open",
            "nelson": "open",
            "sector_a": "open",
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"Integrated R-114 {status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    print(f"children: primary {PRIMARY_ASSERTION_ORACLE}/{PRIMARY_ASSERTION_ORACLE}; independent {INDEPENDENT_ASSERTION_ORACLE}/{INDEPENDENT_ASSERTION_ORACLE}")
    print("exact Bernstein signs: 3981/3981 in each non-importing implementation")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
