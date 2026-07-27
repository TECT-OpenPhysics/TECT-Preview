#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-105 package."""

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
from decimal import Decimal
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CARTAN-RATIONAL-SUBDIVISION-SMART-PATH-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_cartan_rational_subdivision_smart_path_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_cartan_rational_subdivision_smart_path_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-cartan-rational-subdivision-smart-path-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-cartan-rational-subdivision-smart-path-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_cartan_rational_subdivision_smart_path_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-cartan-rational-subdivision-smart-path-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-cartan-rational-subdivision-smart-path-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-cartan-rational-subdivision-smart-path-boundary/result.json"

PRIMARY_ASSERTION_ORACLE = 111
INDEPENDENT_ASSERTION_ORACLE = 111

AUTHORITY_MANIFESTS = {
    "a7": "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "a9": "claims/A9-CLASSII-SMART-PATH-CANCELLATION/classii_smart_path_manifest.json",
    "r085": f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
    "r088": f"claims/{CLAIM}/classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
    "r092": f"claims/{CLAIM}/classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
    "r093": f"claims/{CLAIM}/classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r098": f"claims/{CLAIM}/classii_signed_first_cartan_rational_ridge_boundary_manifest.json",
    "r099": f"claims/{CLAIM}/classii_extended_state_cartan_doob_rational_recovery_manifest.json",
    "r100": f"claims/{CLAIM}/classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
    "r101": f"claims/{CLAIM}/classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
    "r102": f"claims/{CLAIM}/classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r104": f"claims/{CLAIM}/classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
}

PRIMARY_LOAD_BEARING = (
    "one exact K_R",
    "one exact F_6_5",
    "one exact Delta",
    "split exact K_R",
    "split exact F_6_5",
    "split exact Delta",
    "labelled-owner defects cancel",
    "all common-root partitions have same grouped square",
    "closed extended loop has zero grouped charge",
    "edgewise square is a subdivision artefact",
    "heat compensator is necessary",
    "IBP coefficient is strictly negative",
    "critical three-quarter Young threshold",
    "full-budget pointwise minimum diverges",
    "production horizontal coefficient reduces to four a",
    "production horizontal coefficient is positive",
    "top-shell cubic harmonic decomposition",
    "top-shell quintic harmonic decomposition",
    "top-shell sextic average",
    "top-shell projected current stays active",
    "top-shell resolvent range saturation",
    "all-law relative bracket leading ratio",
    "all-law relative bracket requires nonintegrable b",
    "one-pair covariance-normal energy identity",
    "noncentral Gaussian Laplace completion",
    "one-pair mu summability exponent",
    "one-pair alpha-square summability exponent",
    "cross-mode resonance identity",
    "cross-mode resonance has negative production-shaped example",
)

INDEPENDENT_LOAD_BEARING = (
    "independent one exact K_R",
    "independent one exact F_6_5",
    "independent one exact Delta",
    "independent split exact K_R",
    "independent split exact F_6_5",
    "independent split exact Delta",
    "independent defects cancel",
    "independent grouped Cartan quotient",
    "independent closed Cartan charge zero",
    "independent edgewise artefact positive",
    "independent smart-path first variation negative",
    "independent critical Young saturating ratio",
    "independent full-budget pointwise minimum diverges",
    "independent production horizontal coefficient reduces to four a",
    "independent production horizontal coefficient is positive",
    "independent top-shell cubic projection",
    "independent top-shell quintic projection",
    "independent top-shell sextic average",
    "independent top-shell projected current stays active",
    "independent resolvent saturation identity 1",
    "independent resolvent saturation identity 2",
    "independent resolvent saturation identity 3",
    "independent all-law relative bracket ratio 1",
    "independent all-law relative bracket ratio 2",
    "independent all-law relative bracket ratio 3",
    "independent required b dyadic integral grows linearly",
    "independent one-pair covariance-normal identity 1",
    "independent one-pair log-bound derivative 8",
    "independent one-pair mu summability exponent",
    "independent one-pair alpha-square summability exponent",
    "independent cross-mode resonance 4",
    "independent cross-mode negative resonance fixture",
)

NOTE_TOKENS = (
    "R-105",
    "evidence-anchor: theorem-2.1-complete-common-root-cartan-quotient",
    "evidence-anchor: proposition-5.1-rational-owner-subdivision-nogo",
    "evidence-anchor: theorem-6.1-relative-bracket-successor",
    "evidence-anchor: proposition-6.2-all-law-relative-bracket-nogo",
    r"b(t)\ge {3\over t}",
    "Gibbs-law-only or time-integrated",
    "evidence-anchor: theorem-8.1-one-fourier-pair-source-bound",
    r"F_{6.5}",
    r"\mathcal K_R",
    "1600/81",
    r"80\over9",
    r"\mathrm{OVERLAP}_{\rm src}",
    "T4",
)

EXPLORATIONS = {
    "EXP-000263": "advanced",
    "EXP-000264": "failed",
    "EXP-000265": "failed",
    "EXP-000266": "advanced",
    "EXP-000267": "failed",
    "EXP-000268": "advanced",
    "EXP-000269": "failed",
}

NEGATIVE_IDS = (
    "NG-2026-07-28-A13-RATIONAL-TAYLOR-OWNER-SUBDIVISION",
    "NG-2026-07-28-A13-GENERIC-SMART-PATH-MONOTONICITY",
    "NG-2026-07-28-A13-ALL-LAW-POINTWISE-RELATIVE-BRACKET",
    "NG-2026-07-28-A13-FULL-BUDGET-CRITICAL-YOUNG",
    "NG-2026-07-28-A13-ONE-PAIR-PRODUCT-FACTORIZATION",
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


def source_version(path: Path) -> str | None:
    match = re.search(
        r'^(?:__version__|VERSION)\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return None if match is None else match.group(1)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def result_passes(record: dict[str, Any]) -> bool:
    total = record.get("assertions_total")
    names = record.get("assertion_names")
    assertion_rows = record.get("assertions")
    shape_ok = (
        isinstance(names, list)
        and len(names) == total
        and len(set(names)) == total
    ) or (
        isinstance(assertion_rows, list)
        and len(assertion_rows) == total
    )
    return (
        str(record.get("status", "")).upper() == "PASS"
        and isinstance(total, int)
        and total > 0
        and record.get("assertions_passed") == total
        and shape_ok
    )


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
            "tect/a13-cartan-rational-subdivision-smart-path-boundary-primary/1.0",
        ),
        (
            "independent",
            INDEPENDENT,
            INDEPENDENT_RESULT,
            INDEPENDENT_ASSERTION_ORACLE,
            "tect/a13-cartan-rational-subdivision-smart-path-boundary-independent/1.0",
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
    primary_names = set(primary.get("assertion_names", []))
    independent_names = set(independent.get("assertion_names", []))
    for name in PRIMARY_LOAD_BEARING:
        add("load_bearing", f"primary_{name}", name in primary_names, name if name in primary_names else "missing", name)
    for name in INDEPENDENT_LOAD_BEARING:
        add("load_bearing", f"independent_{name}", name in independent_names, name if name in independent_names else "missing", name)

    p = primary.get("results", {}) if isinstance(primary.get("results"), dict) else {}
    i = independent.get("results", {}) if isinstance(independent.get("results"), dict) else {}
    for section in (
        "jets",
        "one_chart",
        "split_sum",
        "one_minus_split",
        "smart_path",
        "relative_bracket_boundary",
    ):
        add("cross_route", f"{section}_exact_match", p.get(section) == i.get(section), [p.get(section), i.get(section)], "exact match")
    shared_verdicts = (
        "common_root_signed_grouping",
        "generic_A9_monotonicity",
        "all_law_relative_A9_bracket",
        "historical_F_6_5_progressive_owner",
        "nelson_q_10_9",
        "sector_a",
        "uniform_overlap_src",
    )
    for key in shared_verdicts:
        actual_pair = [p.get("route_verdicts", {}).get(key), i.get("route_verdicts", {}).get(key)]
        add("cross_route", f"route_verdict_{key}", actual_pair[0] == actual_pair[1], actual_pair, "exact match")
    add(
        "cross_route",
        "all_law_relative_A9_bracket_verdict",
        p.get("route_verdicts", {}).get("all_law_relative_A9_bracket")
        == "failed-production-top-shell-ray",
        p.get("route_verdicts", {}).get("all_law_relative_A9_bracket"),
        "failed-production-top-shell-ray",
    )
    add("cross_route", "fixed_chart_K_R_scoped", p.get("route_verdicts", {}).get("fixed_chart_K_R") == "retained-only-in-declared-regular-scope", p.get("route_verdicts", {}).get("fixed_chart_K_R"), "retained-only-in-declared-regular-scope")

    rational_expectations = {
        ("jets", "bpp0"): "8",
        ("jets", "b1"): "169/81",
        ("jets", "bp1"): "208/81",
        ("jets", "bpp1"): "-2/81",
        ("jets", "b2"): "400/81",
        ("one_chart", "K_R"): "-992/81",
        ("one_chart", "F_6_5"): "-992/81",
        ("one_chart", "Delta"): "1600/81",
        ("split_sum", "K_R"): "355/162",
        ("split_sum", "F_6_5"): "427/162",
        ("split_sum", "Delta"): "1600/81",
        ("one_minus_split", "R_Q"): "-77/18",
        ("one_minus_split", "M_U"): "1516/81",
        ("one_minus_split", "K_R"): "-2339/162",
        ("one_minus_split", "Delta"): "0",
    }
    for (section, key), expected in rational_expectations.items():
        actual = p.get(section, {}).get(key)
        add("rational", f"{section}_{key}", actual == expected, actual, expected)

    cartan_expected = {
        "coarse_grouped_square": "3626",
        "refined_grouped_square": "3626",
        "closed_loop_grouped_square": "0",
        "closed_loop_edgewise_square": "62132",
    }
    for key, expected in cartan_expected.items():
        actual_pair = [p.get("cartan", {}).get(key), i.get("cartan", {}).get(key)]
        add("cartan", key, actual_pair == [expected, expected], actual_pair, [expected, expected])
    add("cartan", "heat_compensator_required", p.get("cartan", {}).get("complete_heat_compensator_required") is True, p.get("cartan", {}).get("complete_heat_compensator_required"), True)

    smart = p.get("smart_path", {})
    for key, expected in {
        "p": "10/9",
        "lambda": "3/20",
        "radial_tilt_a": "4/3",
        "first_variation_factor_times_positive_EY4": "-80/9",
        "generic_monotonicity": False,
        "production_specific_counterexample": False,
    }.items():
        add("smart_path", key, smart.get(key) == expected, smart.get(key), expected)

    pdet = p.get("deterministic_method_boundaries", {})
    idet = i.get("deterministic_method_boundaries", {})
    for key, expected in {
        "critical_three_quarter_threshold": "3/5",
        "full_energy_budget": "9/20",
        "full_sextic_budget": "3/20",
        "pathwise_uniform_coercivity": False,
        "nelson_counterexample": False,
        "upstream_constant_mode_counterterm_slope": "0.0012483343933611451",
    }.items():
        actual_pair = [pdet.get(key), idet.get(key)]
        add("deterministic_boundary", key, actual_pair == [expected, expected], actual_pair, [expected, expected])
    coefficient_gap = abs(
        Decimal(str(pdet.get("constant_mode_minimum_coefficient_decimal", "nan")))
        - Decimal(str(idet.get("constant_mode_minimum_coefficient_decimal", "nan")))
    )
    add("deterministic_boundary", "constant_mode_independent_tolerance", coefficient_gap <= Decimal("1e-14"), str(coefficient_gap), "<=1e-14")

    ppair = p.get("one_fourier_pair", {})
    ipair = i.get("one_fourier_pair", {})
    pair_shared = (
        "alpha_square_summability_exponent",
        "conditional_log_bound",
        "covariance_normal_identity",
        "full_physical_mode_factorization",
        "mu_summability_exponent",
        "t_definition",
        "uniform_in_past_shift",
    )
    for key in pair_shared:
        add("one_pair", f"{key}_match", ppair.get(key) == ipair.get(key), [ppair.get(key), ipair.get(key)], "exact match")
    add("one_pair", "mu_exponent", ppair.get("mu_summability_exponent") == 6, ppair.get("mu_summability_exponent"), 6)
    add("one_pair", "alpha_square_exponent", ppair.get("alpha_square_summability_exponent") == 4, ppair.get("alpha_square_summability_exponent"), 4)
    add("one_pair", "primary_resonance", ppair.get("cross_mode_resonance") == "r^2*u*(6*A+5*u)/4", ppair.get("cross_mode_resonance"), "r^2*u*(6*A+5*u)/4")
    add("one_pair", "independent_resonance", ipair.get("cross_mode_resonance") == "k^2*r^2*u*(6*A+5*u)/4", ipair.get("cross_mode_resonance"), "k^2*r^2*u*(6*A+5*u)/4")
    add("one_pair", "negative_fixture_primary", ppair.get("cross_mode_negative_fixture") == "A=1,u=-1,r=2 gives -1", ppair.get("cross_mode_negative_fixture"), "A=1,u=-1,r=2 gives -1")
    add("one_pair", "negative_fixture_independent", ipair.get("cross_mode_negative_fixture") == "A=1,u=-1,r=2,k=1 gives -1", ipair.get("cross_mode_negative_fixture"), "A=1,u=-1,r=2,k=1 gives -1")

    relative = p.get("relative_bracket_boundary", {})
    for key, expected in {
        "active_horizontal_coefficient": "4*a with pinned a>0",
        "all_law_pointwise_integrable_ab": False,
        "all_law_required_b_lower": "b(t)>=3/t",
        "gibbs_specific_or_time_integrated_bracket": "open",
        "resolvent_range_limit": "A^2*T0*(I+q*t*A^2*T0)^-1 -> P_Ran(T0)/(q*t)",
        "sextic_average": "5/16",
        "top_shell_cubic_projection": "P_J cos(kx)^3=(3/4)cos(kx)",
        "top_shell_quintic_projection": "P_J cos(kx)^5=(10/16)cos(kx)",
    }.items():
        add("relative_bracket", key, relative.get(key) == expected, relative.get(key), expected)

    imports = imported_roots(INDEPENDENT)
    forbidden_imports = sorted(imports & {"numpy", "sympy", "scipy"})
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    add("independence", "forbidden_imports", not forbidden_imports, forbidden_imports, [])
    add("independence", "no_primary_import", PRIMARY.stem not in independent_text, PRIMARY.stem if PRIMARY.stem in independent_text else "absent", "absent")
    add("independence", "fraction_engine", "from fractions import Fraction" in independent_text, "present" if "from fractions import Fraction" in independent_text else "missing", "present")

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
        result_entry = entry.get("result") if isinstance(entry, dict) else None
        if result_path is None:
            add("authority", f"{label}_grandfathered_result", result_entry is None, result_entry, None)
        else:
            result_entry = result_entry if isinstance(result_entry, dict) else {}
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
    add("proof_pdf", "page_count_positive", page_count > 0, page_count, ">0")
    add("proof_pdf", "all_pages_nonempty", nonempty_pages == page_count and page_count > 0, nonempty_pages, page_count)
    add("proof_pdf", "no_fields", fields == 0, fields, 0)
    add("proof_pdf", "title", "Common-root Cartan quotient" in pdf_text, "present" if "Common-root Cartan quotient" in pdf_text else "missing", "present")
    footer_tokens = (
        "R-105",
        "1600",
        "ALL-LAW-POINTWISE-RELATIVE-BRACKET",
        "Gibbs-law-only or time-integrated",
        "OVERLAP",
        "Sector-A closure",
    )
    add("proof_pdf", "scope_tokens", all(token in pdf_text for token in footer_tokens), [token in pdf_text for token in footer_tokens], [True] * len(footer_tokens))
    proof_pdf = manifest.get("proof_pdf", {}) if isinstance(manifest.get("proof_pdf"), dict) else {}
    add("proof_pdf", "manifest_path", proof_pdf.get("path") == repo_path(PDF), proof_pdf.get("path"), repo_path(PDF))
    add("proof_pdf", "manifest_hash", PDF.is_file() and proof_pdf.get("sha256") == digest(PDF), proof_pdf.get("sha256"), digest(PDF) if PDF.is_file() else "file")
    add("proof_pdf", "manifest_pages", proof_pdf.get("pages") == page_count and page_count > 0, proof_pdf.get("pages"), page_count)
    add("proof_pdf", "manifest_size", proof_pdf.get("size_bytes") == (PDF.stat().st_size if PDF.is_file() else -1), proof_pdf.get("size_bytes"), PDF.stat().st_size if PDF.is_file() else -1)
    add("proof_pdf", "manifest_form", proof_pdf.get("form_check") == "PASS", proof_pdf.get("form_check"), "PASS")
    add("proof_pdf", "manifest_overfull", proof_pdf.get("overfull_hbox_count") == 0, proof_pdf.get("overfull_hbox_count"), 0)
    add("proof_pdf", "manifest_visual_qa", proof_pdf.get("visual_qa") == "PASS", proof_pdf.get("visual_qa"), "PASS")

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
        "results_ledger": (REPO / "RESULTS-LEDGER.md", ("R-105", "all-law pointwise", "cross-mode")),
        "claim_card": (CLAIM_DIR / "claim.md", (RESULT_ID, "R-105", "EXP-000269")),
        "status": (CLAIM_DIR / "status.json", ("R-105", "all-law pointwise", "Sector A remains open")),
        "lineage_narrative": (CLAIM_DIR / "lineage-narrative.md", ("R-105", "all-law pointwise", "Gibbs-specific")),
        "gates": (REPO / "claims/GATES.md", ("R-105", "all-law pointwise", "OVERLAP_src")),
        "roadmap": (REPO / "ROADMAP.md", ("R-105", "Gibbs-specific", "OVERLAP_src")),
        "todo": (REPO / "TODO.md", ("T-050", "R-105", "Gibbs-specific")),
        "changelog": (REPO / "CHANGELOG.md", ("R-105", "Cartan", "all-law pointwise")),
        "proof_map": (REPO / "theory/proof-evidence-map.md", ("R-105", "EXP-000263", "EXP-000269")),
        "main_proof": (REPO / "theory/main-proof-line.md", ("R-105", "all-law pointwise", "Sector A remains open")),
        "sector_readme": (REPO / "theory/sector-A-foundation/README.md", ("R-105", "Gibbs-specific", "Sector A remains open")),
        "theorem_map": (REPO / "governance/sector-a-theorem-map.json", ("R-105", "Gibbs-specific", "one-pair")),
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
        ("integrated", "tect/a13-cartan-rational-subdivision-smart-path-boundary-integrated/1.0"),
    ):
        add("contract", f"{label}_schema", contract.get(f"{label}_schema") == expected_schema, contract.get(f"{label}_schema"), expected_schema)
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT), ("integrated", OUTPUT)):
        add("contract", f"{label}_output", contract.get(f"{label}_output") == repo_path(path), contract.get(f"{label}_output"), repo_path(path))

    consequence = manifest.get("consequence", {}) if isinstance(manifest.get("consequence"), dict) else {}
    consequence_expectations = {
        "common_root_cartan_endpoint_quotient": True,
        "regular_cartan_subdivision_transport": True,
        "distinct_root_cartan_estimate": False,
        "rational_labelled_owner_subdivision_invariance": False,
        "rational_complete_endpoint_subdivision_invariance": True,
        "generic_a9_monotonicity": False,
        "all_law_pointwise_relative_bracket": False,
        "gibbs_specific_or_time_integrated_bracket": False,
        "one_fourier_pair_uniform_source_bound": True,
        "full_mode_product_factorization": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
    }
    for key, expected in consequence_expectations.items():
        add("consequence", key, consequence.get(key) is expected, consequence.get(key), expected)

    not_established = manifest.get("claims_not_established", {}) if isinstance(manifest.get("claims_not_established"), dict) else {}
    for key in (
        "distinct_root_cartan",
        "visitwise_rational_owner_bound",
        "gibbs_specific_or_time_integrated_bracket",
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
        "schema": "tect/a13-cartan-rational-subdivision-smart-path-boundary-integrated/1.0",
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
            "R-105 proves the complete common-root Cartan endpoint quotient, exact noninvariance of labelled "
            "rational owners under one production-fibre subdivision, scoped method no-gos, and a uniform "
            "one-Fourier-pair conditional bound. It proves no distinct-root Cartan estimate, visitwise rational "
            "owner estimate, Gibbs-specific or time-integrated relative bracket, OVERLAP_src, Nelson estimate, "
            "removal, interacting measure, tier promotion, or Sector A closure.  The all-finite-entropy-law "
            "pointwise relative bracket is instead disproved at one fixed production cutoff."
        ),
    }
    atomic_json(OUTPUT, payload)
    print(json.dumps({key: payload[key] for key in ("status", "assertions_total", "assertions_passed", "assertions_failed", "run_summary")}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
