#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-106 package."""

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
RESULT_ID = "A13-CLASSII-GIBBS-ENDPOINT-PRODUCTION-MERGE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_gibbs_endpoint_production_merge_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_gibbs_endpoint_production_merge_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-gibbs-endpoint-production-merge-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-gibbs-endpoint-production-merge-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_gibbs_endpoint_production_merge_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-gibbs-endpoint-production-merge-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-gibbs-endpoint-production-merge-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-gibbs-endpoint-production-merge-boundary/result.json"
R105_NOTE = CLAIM_DIR / "notes/classii-cartan-rational-subdivision-smart-path-boundary-260728-260728-v1.1.tex.txt"
R105_PDF = CLAIM_DIR / "notes/classii-cartan-rational-subdivision-smart-path-boundary-260728-260728-v1.1.pdf"
R105_MANIFEST = CLAIM_DIR / "classii_cartan_rational_subdivision_smart_path_boundary_manifest.json"

PRIMARY_ASSERTION_ORACLE = 46
INDEPENDENT_ASSERTION_ORACLE = 59

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r077": f"claims/{CLAIM}/classii_causal_packet_payload_resonance_manifest.json",
    "r082": f"claims/{CLAIM}/classii_stopped_current_far_complete_current_near_reduction_manifest.json",
    "r089": f"claims/{CLAIM}/classii_progressive_covariance_compression_rational_mean_spectral_boundary_manifest.json",
    "r093": f"claims/{CLAIM}/classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r096": f"claims/{CLAIM}/classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
    "r097": f"claims/{CLAIM}/classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
    "r099": f"claims/{CLAIM}/classii_extended_state_cartan_doob_rational_recovery_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
}

PRIMARY_LOAD_BEARING = (
    "endpoint likelihood cancels trace",
    "forward KL orientation",
    "reverse KL orientation",
    "thermodynamic derivative",
    "total time integral is endpoint difference",
    "corrected top-shell u6",
    "R-105 ratio unchanged",
    "constant-ray determinant scale",
    "constant-ray sextic scale",
    "CM payment is lower order",
    "small-sigma leading coefficient",
    "radial Fierz split",
    "radial asymptotic eigenvalue",
    "delta bound factorisation",
    "R-082 radial diagonalisation agrees",
    "quartic raw merge",
    "quadratic trace merge cancels",
    "derivative norm envelope",
    "sextic merge",
    "merge tends to minus infinity",
    "threshold solves target crossing",
    "coherent square retains cross terms",
    "coherent and leaf squares differ",
)

INDEPENDENT_LOAD_BEARING = (
    "forward endpoint KL",
    "reverse endpoint KL",
    "likelihood partition identity",
    "independent thermodynamic integral",
    "corrected u6 factor",
    "bracket/free ratio numerator",
    "d exact",
    "all coefficients positive",
    "global-square radial agreement 4",
    "raw merge 1/3",
    "trace merge 1",
    "derivative envelope 5/2",
    "sextic merge 1",
    "sextic sign 5/2",
    "merge upper bound eventually decreases",
    "merge upper bound negative",
    "outer cube count N=100",
    "coherent cross identity",
    "coherent differs from leaf sum",
)

NOTE_TOKENS = (
    "R-106",
    "evidence-anchor: theorem-2.1-gibbs-endpoint-likelihood",
    "evidence-anchor: theorem-6.1-production-radial-merge-nogo",
    r"{\dd\nu_{J,0}\over\dd\nu_{J,1}}",
    r"\Phi_{J,0}-\Phi_{J,1}",
    r"B_\infty(u)u=4au",
    r"-{15r^2(9r^2+2)\over32}",
    "complete coherent output",
    "root-local Gibbs or coherent-output lower bound",
    r"u_6={3\over20}{5\over16}L^3={3L^3\over64}",
    "NELSON AND SECTOR A OPEN",
)

EXPLORATIONS = {
    "EXP-000270": "advanced",
    "EXP-000271": "failed",
    "EXP-000272": "failed",
    "EXP-000273": "failed",
    "EXP-000274": "advanced",
    "EXP-000275": "advanced",
}

NEGATIVE_IDS = (
    "NG-2026-07-28-A13-TOTAL-A9-TIME-INTEGRATION-IDENTITY",
    "NG-2026-07-28-A13-POINTWISE-ENDPOINT-LIKELIHOOD-COERCIVITY",
    "NG-2026-07-28-A13-PRODUCTION-INPUT-MODE-MERGE-TENSORIZATION",
    "AUDIT-2026-07-28-A13-R105-SEXTIC-COEFFICIENT-CUTOFF-NOTATION",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
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


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def source_version(path: Path) -> str | None:
    match = re.search(
        r'^(?:__version__|VERSION)\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return None if match is None else match.group(1)


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    names = record.get("assertion_names")
    rows = record.get("assertions")
    detailed_shape_ok = (
        isinstance(names, list)
        and isinstance(total, int)
        and len(names) == total
        and len(set(names)) == total
    ) or (isinstance(rows, list) and isinstance(total, int) and len(rows) == total)
    counted_legacy_ok = (
        str(record.get("status", "")).upper() == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and record.get("assertions_failed", 0) == 0
        and (detailed_shape_ok or (not isinstance(names, list) and not isinstance(rows, list)))
    )
    verdict_legacy_ok = str(record.get("verdict", "")).upper().endswith("-PASS")
    return counted_legacy_ok or verdict_legacy_ok


def canonical_results_hash(record: dict[str, Any]) -> str:
    encoded = json.dumps(record.get("results", {}), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def authority_result_path(manifest_path: Path) -> Path | None:
    manifest = load_json(manifest_path)
    contract = manifest.get("run_contract", {})
    output = contract.get("integrated_output") if isinstance(contract, dict) else None
    return REPO / output if output else None


def assertion_names(record: dict[str, Any]) -> set[str]:
    names = record.get("assertion_names")
    if isinstance(names, list):
        return {str(name) for name in names}
    rows = record.get("assertions", [])
    return {str(row.get("name")) for row in rows if isinstance(row, dict)}


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
        (
            "primary",
            PRIMARY,
            PRIMARY_RESULT,
            PRIMARY_ASSERTION_ORACLE,
            "tect/a13-gibbs-endpoint-production-merge-boundary-primary/1.0",
        ),
        (
            "independent",
            INDEPENDENT,
            INDEPENDENT_RESULT,
            INDEPENDENT_ASSERTION_ORACLE,
            "tect/a13-gibbs-endpoint-production-merge-boundary-independent/1.0",
        ),
    ):
        result_path.unlink(missing_ok=True)
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
        )
        add("execution", f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add("execution", f"{label}_fresh_result", result_path.is_file(), repo_path(result_path), "fresh atomic output")
        try:
            record = load_json(result_path)
        except Exception as error:
            record = {}
            add("execution", f"{label}_result_json", False, repr(error), "valid JSON")
        else:
            add("execution", f"{label}_result_json", True, "valid JSON", "valid JSON")
        records[label] = record
        add("execution", f"{label}_passes", result_passes(record), record.get("status"), "PASS")
        add("execution", f"{label}_schema", record.get("schema") == expected_schema, record.get("schema"), expected_schema)
        add("execution", f"{label}_version", record.get("version") == "1.0.0", record.get("version"), "1.0.0")
        add("execution", f"{label}_assertion_count", record.get("assertions_total") == expected_count, record.get("assertions_total"), expected_count)
        names = record.get("assertion_names", [])
        add("execution", f"{label}_assertion_names_complete", isinstance(names, list) and len(names) == expected_count, len(names) if isinstance(names, list) else type(names).__name__, expected_count)
        add("execution", f"{label}_assertion_names_unique", isinstance(names, list) and len(set(names)) == expected_count, len(set(names)) if isinstance(names, list) else type(names).__name__, expected_count)
        actual_hash = canonical_results_hash(record)
        add("execution", f"{label}_results_hash", record.get("results_sha256") == actual_hash, record.get("results_sha256"), actual_hash)

    primary = records["primary"]
    independent = records["independent"]
    primary_names = assertion_names(primary)
    independent_names = assertion_names(independent)
    for name in PRIMARY_LOAD_BEARING:
        add("load_bearing", f"primary_{name}", name in primary_names, name if name in primary_names else "missing", name)
    for name in INDEPENDENT_LOAD_BEARING:
        add("load_bearing", f"independent_{name}", name in independent_names, name if name in independent_names else "missing", name)

    p_results = primary.get("results", {})
    i_results = independent.get("results", {})
    p_derived = p_results.get("derived", {}) if isinstance(p_results, dict) else {}
    i_derived = i_results.get("derived", {}) if isinstance(i_results, dict) else {}
    p_routes = p_results.get("route_verdicts", {}) if isinstance(p_results, dict) else {}
    i_routes = i_results.get("route_verdicts", {}) if isinstance(i_results, dict) else {}
    for key in ("production_a", "production_b", "production_c"):
        add("cross_route", f"{key}_exact_match", p_derived.get(key) == i_derived.get(key), [p_derived.get(key), i_derived.get(key)], "exact match")
    for key, expected in {
        "q": "10/9",
        "corrected_top_shell_u6": "3*L**3/64",
        "forced_all_law_ratio": "3/t_top",
        "quartic_merge": "-r**2/4",
        "sextic_merge": "-15*r**2*(9*r**2 + 2)/32",
    }.items():
        add("exact", key, p_derived.get(key) == expected, p_derived.get(key), expected)
    for key, expected in {
        "corrected_top_shell_u6_factor": "3/64",
        "quartic_merge": "-1/4*r^2",
        "sextic_merge": "-15/32*r^2*(9*r^2+2)",
    }.items():
        add("exact", f"independent_{key}", i_derived.get(key) == expected, i_derived.get(key), expected)
    for key, expected in {
        "total_time_integration_without_root_local_bound": "tautological-endpoint-identity",
        "pointwise_endpoint_likelihood_sextic_cm_coercivity": "failed-constant-ray",
        "input_mode_leaf_tensorization": "failed-exact-production-1-to-2-merge",
        "leafwise_sextic_merge_repair": "failed-not-superadditive",
        "coherent_output_frequency_square": "retained-exact-coordinate",
        "nelson": "open",
        "sector_a": "open",
    }.items():
        add("route", key, p_routes.get(key) == expected, p_routes.get(key), expected)
    add("route", "independent_endpoint_boundary", i_routes.get("endpoint_likelihood_identity") == "exact-boundary-only", i_routes.get("endpoint_likelihood_identity"), "exact-boundary-only")
    add("route", "independent_nelson_open", i_routes.get("nelson") == "open", i_routes.get("nelson"), "open")
    add("route", "independent_sector_a_open", i_routes.get("sector_a") == "open", i_routes.get("sector_a"), "open")

    imports = imported_roots(INDEPENDENT)
    forbidden_imports = sorted(imports & {"numpy", "sympy", "scipy"})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "forbidden_imports", not forbidden_imports, forbidden_imports, [])
    add("independence", "no_primary_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "fraction_engine", "from fractions import Fraction" in independent_text, "present" if "from fractions import Fraction" in independent_text else "missing", "present")
    add("independence", "custom_laurent_engine", "def multiply(left: Laurent, right: Laurent)" in independent_text, "present" if "def multiply(left: Laurent, right: Laurent)" in independent_text else "missing", "present")

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest", "manifest_json", False, repr(error), "valid JSON")
    else:
        add("manifest", "manifest_json", True, "valid JSON", "valid JSON")
    add("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "tier_t4", [manifest.get("tier_before"), manifest.get("tier_after")] == ["T4", "T4"], [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest", "proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("manifest", "status_boundary", "BOUNDARY" in str(manifest.get("status", "")) and "OPEN" in str(manifest.get("status", "")), manifest.get("status"), "contains BOUNDARY and OPEN")
    add("manifest", "scope_fixed_cutoff", "Finite cutoff" in str(manifest.get("scope", "")), manifest.get("scope"), "contains Finite cutoff")
    add("manifest", "no_overclaim_text", all(token in str(manifest.get("no_overclaim", "")) for token in ("Nelson", "Sector A", "does not prove")), manifest.get("no_overclaim"), "Nelson/Sector A/do-not-prove boundary")

    sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
    for label, path in (
        ("primary", PRIMARY),
        ("independent", INDEPENDENT),
        ("verifier", Path(__file__).resolve()),
        ("proof_note", NOTE),
    ):
        entry = sources.get(label, {}) if isinstance(sources.get(label), dict) else {}
        add("manifest", f"{label}_path", entry.get("path") == repo_path(path), entry.get("path"), repo_path(path))
        expected_hash = digest(path) if path.is_file() else "file"
        add("manifest", f"{label}_hash", path.is_file() and entry.get("sha256") == expected_hash, entry.get("sha256"), expected_hash)
        expected_version = "1.0" if label == "proof_note" else source_version(path)
        add("manifest", f"{label}_version", entry.get("version") == expected_version, entry.get("version"), expected_version)

    authority_root = manifest.get("authority", {}) if isinstance(manifest.get("authority"), dict) else {}
    for label, relative_path in AUTHORITY_MANIFESTS.items():
        path = REPO / relative_path
        entry = authority_root.get(label, {}) if isinstance(authority_root.get(label), dict) else {}
        manifest_entry = entry.get("manifest", {}) if isinstance(entry.get("manifest"), dict) else {}
        add("authority", f"{label}_manifest_exists", path.is_file(), repo_path(path), "file")
        add("authority", f"{label}_manifest_path", manifest_entry.get("path") == repo_path(path), manifest_entry.get("path"), repo_path(path))
        expected_manifest_hash = digest(path) if path.is_file() else "file"
        add("authority", f"{label}_manifest_hash", path.is_file() and manifest_entry.get("sha256") == expected_manifest_hash, manifest_entry.get("sha256"), expected_manifest_hash)
        try:
            result_path = authority_result_path(path)
        except Exception as error:
            result_path = None
            add("authority", f"{label}_manifest_contract", False, repr(error), "readable")
        else:
            add("authority", f"{label}_manifest_contract", True, "readable", "readable")
        result_entry = entry.get("result", {}) if isinstance(entry.get("result"), dict) else {}
        if result_path is not None:
            add("authority", f"{label}_result_exists", result_path.is_file(), repo_path(result_path), "file")
            add("authority", f"{label}_result_path", result_entry.get("path") == repo_path(result_path), result_entry.get("path"), repo_path(result_path))
            expected_result_hash = digest(result_path) if result_path.is_file() else "file"
            add("authority", f"{label}_result_hash", result_path.is_file() and result_entry.get("sha256") == expected_result_hash, result_entry.get("sha256"), expected_result_hash)
            try:
                authority_record = load_json(result_path)
            except Exception as error:
                add("authority", f"{label}_result_pass", False, repr(error), "PASS")
            else:
                add("authority", f"{label}_result_pass", result_passes(authority_record), authority_record.get("status"), "PASS")

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.is_file() else ""
    note_scan = normalized(note_text)
    add("proof_note", "exists", NOTE.is_file(), repo_path(NOTE), "file")
    for index, token in enumerate(NOTE_TOKENS):
        add("proof_note", f"token_{index:02d}", token in note_scan, token if token in note_scan else "missing", token)
    add("proof_note", "no_replacement", "\ufffd" not in note_text, note_text.count("\ufffd"), 0)
    add("proof_note", "no_bare_qquad", re.search(r"(?<!\\)qquad", note_text) is None, "absent" if re.search(r"(?<!\\)qquad", note_text) is None else "present", "absent")
    add("proof_note", "fragment", "\\documentclass" not in note_text, "fragment", "fragment")

    add("proof_pdf", "exists", PDF.is_file(), repo_path(PDF), "file")
    page_count = 0
    fields = -1
    nonempty_pages = 0
    pdf_text = ""
    if PDF.is_file():
        reader = PdfReader(PDF)
        page_count = len(reader.pages)
        fields = len(reader.get_fields() or {})
        page_texts = [(page.extract_text() or "") for page in reader.pages]
        nonempty_pages = sum(bool(value.strip()) for value in page_texts)
        pdf_text = normalized("\n".join(page_texts))
    add("proof_pdf", "page_count", page_count == 8, page_count, 8)
    add("proof_pdf", "all_pages_nonempty", nonempty_pages == page_count and page_count > 0, nonempty_pages, page_count)
    add("proof_pdf", "no_fields", fields == 0, fields, 0)
    add("proof_pdf", "title", "Gibbs endpoint likelihood" in pdf_text, "present" if "Gibbs endpoint likelihood" in pdf_text else "missing", "present")
    footer_tokens = ("R-106", "PRODUCTION-INPUT-MODE", "3 L^3", "Nelson", "Sector-A closure")
    add("proof_pdf", "scope_tokens", all(token in pdf_text for token in footer_tokens), [token in pdf_text for token in footer_tokens], [True] * len(footer_tokens))
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pages", proof_pdf.get("pages") == page_count == 8, proof_pdf.get("pages"), page_count)
    add("proof_pdf", "manifest_size", proof_pdf.get("size_bytes") == (PDF.stat().st_size if PDF.is_file() else -1), proof_pdf.get("size_bytes"), PDF.stat().st_size if PDF.is_file() else -1)
    add("proof_pdf", "manifest_form", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
    add("proof_pdf", "manifest_overfull", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

    r105_note_text = R105_NOTE.read_text(encoding="utf-8") if R105_NOTE.is_file() else ""
    add("correction", "r105_u6_corrected", r"u_6={3\over20}{5\over16}L^3={3L^3\over64}" in normalized(r105_note_text), "present" if r"u_6={3\over20}{5\over16}L^3={3L^3\over64}" in normalized(r105_note_text) else "missing", "present")
    add("correction", "r105_old_u6_absent", r"5\gamma L^3\over96" not in r105_note_text, "absent" if r"5\gamma L^3\over96" not in r105_note_text else "present", "absent")
    add("correction", "r105_cutoff_N", r"V_N^{\rm ren}" in r105_note_text and r"N=2^J" in r105_note_text, [r"V_N^{\rm ren}" in r105_note_text, r"N=2^J" in r105_note_text], [True, True])
    try:
        r105_manifest = load_json(R105_MANIFEST)
    except Exception as error:
        r105_manifest = {}
        add("correction", "r105_manifest_json", False, repr(error), "valid JSON")
    else:
        add("correction", "r105_manifest_json", True, "valid JSON", "valid JSON")
    r105_sources = r105_manifest.get("sources", {}) if isinstance(r105_manifest.get("sources"), dict) else {}
    add("correction", "r105_note_hash", r105_sources.get("proof_note", {}).get("sha256") == digest(R105_NOTE), r105_sources.get("proof_note", {}).get("sha256"), digest(R105_NOTE))
    r105_pdf_entry = r105_manifest.get("proof_pdf", {}) if isinstance(r105_manifest.get("proof_pdf"), dict) else {}
    add("correction", "r105_pdf_hash", r105_pdf_entry.get("sha256") == digest(R105_PDF), r105_pdf_entry.get("sha256"), digest(R105_PDF))
    add("correction", "r105_pdf_size", r105_pdf_entry.get("size_bytes") == R105_PDF.stat().st_size, r105_pdf_entry.get("size_bytes"), R105_PDF.stat().st_size)

    exploration_rows: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("id") in EXPLORATIONS:
            exploration_rows[record["id"]] = record
    for exploration, verdict in EXPLORATIONS.items():
        record = exploration_rows.get(exploration, {})
        add("explorations", f"{exploration}_present", bool(record), record.get("id"), exploration)
        add("explorations", f"{exploration}_verdict", record.get("verdict") == verdict, record.get("verdict"), verdict)
        add("explorations", f"{exploration}_claim_ref", CLAIM in record.get("claim_ids", []), record.get("claim_ids", []), f"contains {CLAIM}")
        formal_results = record.get("formal_refs", {}).get("results", [])
        add("explorations", f"{exploration}_authority_refs", bool(formal_results), formal_results, "nonempty predecessor/result authorities")

    negative_scan = normalized((REPO / "negative-results/registry.md").read_text(encoding="utf-8"))
    for negative_id in NEGATIVE_IDS:
        add("negative", negative_id, negative_id in negative_scan, negative_id if negative_id in negative_scan else "missing", negative_id)

    surface_tokens = {
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-106", "endpoint likelihood", "coherent output")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "R-106", "EXP-000274")),
        "status": (CLAIM_DIR / "status.json", ("R-106", "coherent output", "Sector A remains open")),
        "lineage_narrative": (CLAIM_DIR / "lineage-narrative.md", ("R-106", "endpoint likelihood", "coherent output")),
        "gates": (REPO / "claims/GATES.md", ("R-106", "coherent output", "OVERLAP_src")),
        "roadmap": (REPO / "ROADMAP.md", ("R-106", "Gibbs", "OVERLAP_src")),
        "todo": (REPO / "TODO.md", ("T-050", "R-106", "coherent output")),
        "changelog": (REPO / "CHANGELOG.md", ("R-106", "endpoint likelihood", "production merge")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-106", "EXP-000270", "EXP-000274")),
        "main_proof": (REPO / "theory/main-proof-line.md", ("R-106", "coherent output", "Sector A remains open")),
        "sector_readme": (REPO / "theory/sector-A-foundation/README.md", ("R-106", "coherent output", "Sector A remains open")),
        "sector_a": (
            REPO / "theory/sectors/A.md",
            (
                CLAIM,
                "NG-2026-07-28-A13-TOTAL-A9-TIME-INTEGRATION-IDENTITY",
                "NG-2026-07-28-A13-PRODUCTION-INPUT-MODE-MERGE-TENSORIZATION",
            ),
        ),
        "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-106", "coherent output", "endpoint likelihood")),
    }
    for label, (path, tokens) in surface_tokens.items():
        scan = normalized(path.read_text(encoding="utf-8")) if path.is_file() else ""
        add("surfaces", f"{label}_exists", path.is_file(), repo_path(path), "file")
        for index, token in enumerate(tokens):
            add("surfaces", f"{label}_token_{index}", token in scan, token if token in scan else "missing", token)

    try:
        status = load_json(CLAIM_DIR / "status.json")
    except Exception as error:
        status = {}
        add("surfaces", "status_json", False, repr(error), "valid JSON")
    else:
        add("surfaces", "status_json", True, "valid JSON", "valid JSON")
    add("surfaces", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")

    contract = manifest.get("run_contract", {}) if isinstance(manifest.get("run_contract"), dict) else {}
    canonical_command = contract.get("command", "")
    add("surfaces", "status_reproduction", status.get("reproduction", {}).get("command") == canonical_command, status.get("reproduction", {}).get("command"), canonical_command)
    add("contract", "primary_count", contract.get("primary_assertions") == primary.get("assertions_total") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent_count", contract.get("independent_assertions") == independent.get("assertions_total") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    for label, expected_schema in (
        ("primary", primary.get("schema")),
        ("independent", independent.get("schema")),
        ("integrated", "tect/a13-gibbs-endpoint-production-merge-boundary-integrated/1.0"),
    ):
        add("contract", f"{label}_schema", contract.get(f"{label}_schema") == expected_schema, contract.get(f"{label}_schema"), expected_schema)
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT), ("integrated", OUTPUT)):
        add("contract", f"{label}_output", contract.get(f"{label}_output") == repo_path(path), contract.get(f"{label}_output"), repo_path(path))

    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "gibbs_endpoint_likelihood_identity": True,
        "thermodynamic_integration_identity": True,
        "independent_root_local_gibbs_bound": False,
        "pointwise_endpoint_likelihood_coercivity": False,
        "exact_production_radial_fierz": True,
        "input_mode_leaf_tensorization": False,
        "leafwise_sextic_merge_repair": False,
        "coherent_output_frequency_coordinate": True,
        "full_root_local_coherent_packet_bound": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)

    not_established = manifest.get("claims_not_established", {}) if isinstance(manifest.get("claims_not_established"), dict) else {}
    for key in (
        "gibbs_root_local_bound",
        "full_root_local_coherent_packet_bound",
        "full_overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    ):
        add("no_overclaim", key, not_established.get(key) is False, not_established.get(key), False)

    add("manifest", "negative_ids", manifest.get("negative_results") == list(NEGATIVE_IDS), manifest.get("negative_results"), list(NEGATIVE_IDS))
    add("manifest", "exploration_ids", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))

    final_integrated_count = len(rows) + 2
    add("contract", "integrated_count", contract.get("integrated_assertions") == final_integrated_count, contract.get("integrated_assertions"), final_integrated_count)
    aggregate = primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + final_integrated_count
    add("contract", "aggregate_count", contract.get("aggregate_assertions") == aggregate, contract.get("aggregate_assertions"), aggregate)

    passed = sum(row["status"] == "PASS" for row in rows)
    if count_only:
        print(f"INTEGRATED ASSERTIONS PLANNED: {len(rows)}")
        print(f"AGGREGATE ASSERTIONS PLANNED: {aggregate}")
        print(f"CURRENT PASS: {passed}/{len(rows)}")
        return 0

    payload = {
        "schema": "tect/a13-gibbs-endpoint-production-merge-boundary-integrated/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "source_hashes": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "verifier": digest(Path(__file__).resolve()),
            "proof_note": digest(NOTE) if NOTE.is_file() else None,
            "proof_pdf": digest(PDF) if PDF.is_file() else None,
            "manifest": digest(MANIFEST) if MANIFEST.is_file() else None,
        },
        "run_summary": {
            "primary": primary.get("assertions_total"),
            "independent": independent.get("assertions_total"),
            "integrated": len(rows),
            "aggregate": primary.get("assertions_total", 0) + independent.get("assertions_total", 0) + len(rows),
        },
        "no_overclaim": (
            "R-106 proves exact Gibbs endpoint-likelihood, entropy, thermodynamic-integration, "
            "production radial Fierz, and fixed-cutoff 1:2 merge identities. It retires pointwise "
            "endpoint-likelihood coercivity, deterministic input-mode leaf tensorization, and a "
            "leafwise sextic repair. It does not prove the root-local coherent Gibbs packet, "
            "OVERLAP_src, Nelson, removals, an interacting measure, tier promotion, or Sector A closure."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
