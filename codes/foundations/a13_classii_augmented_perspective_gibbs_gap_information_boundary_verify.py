#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the R-093 A13 boundary package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import hashlib
import ast
import json
import math
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
RESULT_ID = "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM

PRIMARY = REPO / "codes/foundations/a13_classii_augmented_perspective_gibbs_gap_information_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_augmented_perspective_gibbs_gap_information_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-27-primary-augmented-perspective-gibbs-gap-information-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-27-independent-augmented-perspective-gibbs-gap-information-boundary/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-27-integrated-augmented-perspective-gibbs-gap-information-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

AUTHORITY = {
    "a7_renormalised_energy": (
        REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
        REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/runs/2026-07-20-integrated-renormalised-energy/result.json",
    ),
    "a12_source_square": (
        REPO / "claims/A12-CLASSII-SOURCE-SQUARE-REDUCTION/classii_source_square_reduction_manifest.json",
        REPO / "claims/A12-CLASSII-SOURCE-SQUARE-REDUCTION/runs/2026-07-21-integrated-source-square/result.json",
    ),
    "r081_temporal": (
        CLAIM_DIR / "classii_cartan_tail_adapted_near_temporal_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-tail-adapted-near-temporal-reduction/result.json",
    ),
    "r087_core": (
        CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json",
    ),
    "r091_coefficient": (
        CLAIM_DIR / "classii_projected_cartan_full_frame_temporal_boundary_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-projected-cartan-full-frame-temporal-boundary/result.json",
    ),
    "r092_perspective": (
        CLAIM_DIR / "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
        CLAIM_DIR / "runs/2026-07-25-integrated-normalized-cartan-perspective-covariance-frontier/result.json",
    ),
}

NEGATIVE_RESULTS = (
    "AUDIT-2026-07-27-A13-R092-AUGMENTED-PRODUCTION-COVARIANCE",
    "NG-2026-07-27-A13-LOCAL-PERSPECTIVE-PAID-SCALING",
    "NG-2026-07-27-A13-COEFFICIENT-REVEAL-FREE-CONDITIONING",
    "NG-2026-07-27-A13-FIXED-SOURCE-CHART-GIBBS-ATTAINMENT",
    "NG-2026-07-27-A13-FIBRE-ENTROPY-UNIFORM-RESERVE",
    "NG-2026-07-27-A13-CAUSAL-ORTHOGONAL-QR",
)

EXPLORATIONS = tuple(f"EXP-{index:06d}" for index in range(180, 192))

EXPLORATION_VERDICTS = {
    "EXP-000180": "advanced",
    "EXP-000181": "failed",
    "EXP-000182": "failed",
    "EXP-000183": "failed",
    "EXP-000184": "failed",
    "EXP-000185": "advanced",
    "EXP-000186": "failed",
    "EXP-000187": "failed",
    "EXP-000188": "inconclusive",
    "EXP-000189": "advanced",
    "EXP-000190": "advanced",
    "EXP-000191": "inconclusive",
}

NOTE_TOKENS = (
    "R-093",
    "complete augmented one-reveal normal form",
    "evidence-anchor: section-2-unconditional-augmented-normal-form",
    "Schur complement of $B+2R",
    "\\Theta_R(B)\\preceq B",
    "All spaces in this theorem are finite-dimensional",
    "\\mathbb E_{\\mathcal F}\\|B\\|",
    "\\mathbb E_{\\mathcal F}\\|Bz\\|",
    "even-reveal covariance classifier",
    "positive-branch inverse",
    "The smallest genuine paid lift is coercive",
    "I(G;B)=+\\infty",
    "Gibbs-gap identity",
    "source-union/CORE equality",
    "evidence-anchor: theorem-6.2-source-union-core-equality",
    "R-087 CORE payoff hypotheses",
    "0<Z_J<\\infty",
    "\\mathbb E V_J^{\\rm ren}(X_J)=0",
    "undefined $\\infty-\\infty$ subtraction is intended",
    "near-minimiser rigidity",
    "Q\\hbox{ block diagonal}",
    "2^{j-4k}",
    "Enhanced-model polynomial BG criterion",
    "evidence-anchor: section-9-enhanced-model-polynomial-bg-criterion",
    "Z_{\\tau,J}\\ge0",
    "\\inf_J\\mathbb E V_J^{\\rm ren}(X_J)>-\\infty",
    "weighted summability",
    "only the arithmetic ledger",
    "not a new transfer theorem",
    "The largest finite required moment in this finite inherited ledger is $30$",
    "root-local paid production",
    "Complete uniform $H_N$",
    "Sector A remain",
    "Tier stays T4",
    "is nonzero with positive probability",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
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
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return None if match is None else match.group(1)


def authority_passes(record: dict[str, Any], expected_schema: str) -> bool:
    if record.get("schema") != expected_schema:
        return False
    if expected_schema == "tect/a7-classii-renormalised-energy-integrated-result/1.1":
        aggregate = record.get("assertion_summary", {}).get("aggregate", {})
        return (
            record.get("verdict") == "A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-PASS"
            and record.get("failures") == []
            and record.get("assertion_summary", {}).get("count_contract") is True
            and isinstance(aggregate.get("passed"), int)
            and aggregate.get("passed") == aggregate.get("total")
            and aggregate.get("total", 0) > 0
        )
    if expected_schema == "tect/a12-classii-source-square-integrated-result/1.0":
        assertion_rows = record.get("integrated_assertions", [])
        return (
            record.get("status") == "PASS"
            and record.get("failed") == 0
            and isinstance(record.get("assertion_count"), int)
            and record.get("passed") == record.get("assertion_count")
            and bool(assertion_rows)
            and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertion_rows)
        )
    passed = record.get("assertions_passed")
    total = record.get("assertions_total")
    assertion_rows = record.get("assertions", record.get("integrated_assertions", []))
    return (
        record.get("status") == "PASS"
        and isinstance(passed, int)
        and isinstance(total, int)
        and total > 0
        and passed == total
        and len(assertion_rows) == total
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertion_rows)
    )


def assertion_actual(record: dict[str, Any], name: str) -> Any:
    for row in record.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row.get("actual")
    return None


def main() -> int:
    count_only = "--count-only" in sys.argv
    rows: list[dict[str, Any]] = []

    def add(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    result_paths = {"primary": PRIMARY_RESULT, "independent": INDEPENDENT_RESULT}
    for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
        result_paths[label].unlink(missing_ok=True)
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
        )
        add(f"{label}_process_exit", completed.returncode == 0, completed.returncode, 0)
        add(f"{label}_fresh_result", result_paths[label].exists(), repo_path(result_paths[label]), "fresh atomic output exists")

    try:
        manifest = load_json(MANIFEST)
    except Exception as error:
        manifest = {}
        add("manifest_load", False, repr(error), "valid JSON")
    else:
        add("manifest_load", True, "valid JSON", "valid JSON")

    records: dict[str, dict[str, Any]] = {}
    for label, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        try:
            records[label] = load_json(path)
        except Exception as error:
            records[label] = {}
            add(f"{label}_result_load", False, repr(error), "valid JSON")
        else:
            add(f"{label}_result_load", True, "valid JSON", "valid JSON")

    contract = manifest.get("run_contract", {})
    expected_counts = {
        "primary": contract.get("primary_assertions"),
        "independent": contract.get("independent_assertions"),
    }
    expected_schemas = {
        "primary": "tect/a13-augmented-perspective-gibbs-gap-information-boundary-primary/1.0",
        "independent": "tect/a13-augmented-perspective-gibbs-gap-information-boundary-independent/1.0",
    }
    for label, record in records.items():
        add(f"{label}_status", record.get("status") == "PASS", record.get("status"), "PASS")
        add(
            f"{label}_passed_total",
            record.get("assertions_passed") == record.get("assertions_total"),
            [record.get("assertions_passed"), record.get("assertions_total")],
            "equal",
        )
        add(
            f"{label}_manifest_count",
            record.get("assertions_total") == expected_counts[label],
            record.get("assertions_total"),
            expected_counts[label],
        )
        add(f"{label}_claim", record.get("claim_id") == CLAIM, record.get("claim_id"), CLAIM)
        add(f"{label}_result_id", record.get("result_id") == RESULT_ID, record.get("result_id"), RESULT_ID)
        add(f"{label}_schema", record.get("schema") == expected_schemas[label], record.get("schema"), expected_schemas[label])
        add(f"{label}_version", record.get("version") == "1.0.0", record.get("version"), "1.0.0")
        assertion_rows = record.get("assertions", [])
        assertion_names = [row.get("name") for row in assertion_rows if isinstance(row, dict)]
        add(
            f"{label}_assertion_list_count",
            len(assertion_rows) == record.get("assertions_total"),
            [len(assertion_rows), record.get("assertions_total")],
            "equal",
        )
        add(
            f"{label}_assertion_names_unique",
            len(assertion_names) == len(set(assertion_names)) == len(assertion_rows),
            [len(assertion_names), len(set(assertion_names)), len(assertion_rows)],
            "all rows named uniquely",
        )
        add(
            f"{label}_every_assertion_pass",
            bool(assertion_rows) and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertion_rows),
            [row.get("name") for row in assertion_rows if not isinstance(row, dict) or row.get("status") != "PASS"],
            [],
        )

    primary = records.get("primary", {})
    independent = records.get("independent", {})
    primary_names = {row.get("name") for row in primary.get("assertions", []) if isinstance(row, dict)}
    independent_names = {row.get("name") for row in independent.get("assertions", []) if isinstance(row, dict)}
    required_primary = {
        "authority_r081_tokens",
        "authority_r087_tokens",
        "authority_r091_tokens",
        "authority_r092_tokens",
        "radial_derivative_positive_polynomial",
        "coefficient_positive_branch_monotone",
        "perspective_pointwise_identity",
        "finite_density_eta_1_10",
        "finite_density_eta_1_2",
        "finite_density_eta_7",
        "gaussian_density_negative",
        "fixed_one_block_gap",
        "gibbs_gap_identity",
        "gibbs_gap_two_coefficients",
        "near_minimizer_each_gap_bound",
        "equiprobable_reveal_mi_32",
        "deterministic_overlap_entropy_formula_fixture",
        "feedback_overlap_entropy_formula_fixture",
        "bg_maximum_required_moment",
        "bg_critical_pair_1",
        "bg_critical_pair_2",
        "cutoff_two_control_margin_positive",
        "cutoff_two_bound_constant_finite",
    }
    required_independent = {
        "independent_matrix_perspective_identity",
        "independent_theta_positive_semidefinite_before_clipping",
        "independent_unconditional_normal_form",
        "independent_gaussian_covariance_negative",
        "independent_one_chart_obstruction",
        "independent_quantile_information_19",
        "independent_bg_all_slacks_positive",
        "independent_bg_maximum_moment",
        "independent_bg_critical_rows",
        "independent_unsubtracted_normal_form",
        "independent_covariance_subtraction_load_bearing",
        "independent_lower_orthogonal_gram_excludes_c_-1",
        "independent_lower_orthogonal_gram_excludes_c_1",
        "independent_cutoff_two_paid_margin",
        "independent_cutoff_two_lower_constant",
    }
    add("primary_required_assertions", required_primary <= primary_names, sorted(required_primary - primary_names), [])
    add(
        "independent_required_assertions",
        required_independent <= independent_names,
        sorted(required_independent - independent_names),
        [],
    )

    p_derived = primary.get("derived", {})
    i_derived = independent.get("derived", {})
    add(
        "exact_finite_density_crosscheck",
        p_derived.get("finite_density_times_P_over_e")
        == i_derived.get("finite_density_times_P_over_e")
        == "-1236/21125",
        [p_derived.get("finite_density_times_P_over_e"), i_derived.get("finite_density_times_P_over_e")],
        "-1236/21125",
    )
    add(
        "gaussian_reciprocal_crosscheck",
        math.isclose(float(p_derived.get("gaussian_reciprocal", math.nan)), float(i_derived.get("gaussian_reciprocal", math.inf)), rel_tol=0.0, abs_tol=1e-10),
        [p_derived.get("gaussian_reciprocal"), i_derived.get("gaussian_reciprocal")],
        "agreement within 1e-10",
    )
    p_cutoff = p_derived.get("cutoff_two_paid_coercivity", {})
    i_cutoff = i_derived.get("cutoff_two_paid_coercivity", {})
    for key in (
        "beta_operator",
        "gradient_covariance_trace",
        "negative_quadratic_constant",
        "field_covariance_trace",
        "shell_symbol_minimum",
        "control_map_bound",
        "paid_control_margin",
        "lower_bound_constant",
    ):
        add(
            f"cutoff_two_{key}_crosscheck",
            math.isclose(float(p_cutoff.get(key, math.nan)), float(i_cutoff.get(key, math.inf)), rel_tol=0.0, abs_tol=2e-12),
            [p_cutoff.get(key), i_cutoff.get(key)],
            "agreement within 2e-12",
        )
    add("cutoff_two_margin_test_oracle", float(p_cutoff.get("paid_control_margin", -math.inf)) > 0.388, p_cutoff.get("paid_control_margin"), "> 0.388")
    add("cutoff_two_constant_test_oracle", float(p_cutoff.get("lower_bound_constant", math.inf)) < 12.0, p_cutoff.get("lower_bound_constant"), "< 12")
    beta_operator = float(p_cutoff.get("beta_operator", math.nan))
    gradient_trace = float(p_cutoff.get("gradient_covariance_trace", math.nan))
    negative_constant = float(p_cutoff.get("negative_quadratic_constant", math.nan))
    field_trace = float(p_cutoff.get("field_covariance_trace", math.nan))
    shell_minimum = float(p_cutoff.get("shell_symbol_minimum", math.nan))
    control_bound = float(p_cutoff.get("control_map_bound", math.nan))
    paid_margin = float(p_cutoff.get("paid_control_margin", math.nan))
    lower_constant = float(p_cutoff.get("lower_bound_constant", math.nan))
    add("cutoff_two_c2_identity", math.isclose(negative_constant, 0.5 * beta_operator * gradient_trace, rel_tol=0.0, abs_tol=2e-14), negative_constant - 0.5 * beta_operator * gradient_trace, 0.0)
    add("cutoff_two_control_map_identity", math.isclose(control_bound, 2.0 / shell_minimum, rel_tol=0.0, abs_tol=2e-13), control_bound - 2.0 / shell_minimum, 0.0)
    add("cutoff_two_paid_margin_identity", math.isclose(paid_margin, 9.0 / 20.0 - 2.0 * negative_constant * control_bound, rel_tol=0.0, abs_tol=2e-13), paid_margin - (9.0 / 20.0 - 2.0 * negative_constant * control_bound), 0.0)
    add("cutoff_two_lower_constant_identity", math.isclose(lower_constant, 2.0 * negative_constant * field_trace, rel_tol=0.0, abs_tol=2e-12), lower_constant - 2.0 * negative_constant * field_trace, 0.0)
    add("bg_moment_crosscheck", p_derived.get("bg_maximum_required_moment") == i_derived.get("bg_maximum_required_moment") == "30", [p_derived.get("bg_maximum_required_moment"), i_derived.get("bg_maximum_required_moment")], "30")
    gibbs_coefficient = float(assertion_actual(primary, "gibbs_gap_two_coefficients") or math.nan)
    add("gibbs_coefficients", math.isclose(gibbs_coefficient, 0.9, rel_tol=0.0, abs_tol=1e-15), gibbs_coefficient, 0.9)
    one_chart_actual = assertion_actual(primary, "fixed_one_block_gap")
    one_chart_gap = one_chart_actual[-1] if isinstance(one_chart_actual, list) and one_chart_actual else math.nan
    add("one_chart_infimum_exact", p_derived.get("fixed_one_block_quadratic_infimum") == 0.5, p_derived.get("fixed_one_block_quadratic_infimum"), 0.5)
    add("one_chart_gap_positive", float(one_chart_gap) > 0.16, one_chart_gap, "> 0.16")
    add("matrix_normal_form_error", float(i_derived.get("matrix_normal_form_max_error", math.inf)) < 2e-11, i_derived.get("matrix_normal_form_max_error"), "< 2e-11")

    add("manifest_claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest_result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest_schema", manifest.get("schema") == "tect/a13-augmented-perspective-gibbs-gap-information-boundary/1.0", manifest.get("schema"), "tect/a13-augmented-perspective-gibbs-gap-information-boundary/1.0")
    add("manifest_package_version", manifest.get("package_version") == "1.0.0", manifest.get("package_version"), "1.0.0")
    add("manifest_proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("manifest_tiers", manifest.get("tier_before") == manifest.get("tier_after") == "T4", [manifest.get("tier_before"), manifest.get("tier_after")], ["T4", "T4"])
    add("manifest_r093", manifest.get("consequence", {}).get("result_ledger_id") == "R-093", manifest.get("consequence", {}).get("result_ledger_id"), "R-093")
    add("manifest_t4_open", "T4" in str(manifest.get("status")) and "OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 with open gates")
    consequences = manifest.get("consequence", {})
    add("consequence_current_child", consequences.get("current_child") == "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET", consequences.get("current_child"), "A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET")
    for key in (
        "unconditional_augmented_normal_form",
        "even_reveal_covariance_classifier",
        "smooth_production_sign_fixture",
        "local_sign_independent_of_fixed_perspective_payment",
        "cutoff_two_paid_coercivity",
        "coefficient_reveal_information_price",
        "smooth_reveal_mutual_information_infinite",
        "gibbs_gap_identity",
        "source_union_core_equality",
        "near_minimizer_entropy_rigidity",
        "enhanced_model_bg_sufficient_criterion",
    ):
        add(f"consequence_{key}", consequences.get(key) is True, consequences.get(key), True)
    for key in (
        "local_fixture_is_paid_h_n_counterexample",
        "cutoff_two_uniform_in_cutoff",
        "fixed_source_chart_attains_core",
        "uniform_fibre_entropy_reserve",
        "causal_orthogonal_qr",
        "uniform_h_n",
        "exact_h_a_packet_assembly",
        "full_overlap_src",
        "nelson",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
    ):
        add(f"consequence_{key}_false", consequences.get(key) is False, consequences.get(key), False)
    add("consequence_cutoff_two_paid_margin", math.isclose(float(consequences.get("cutoff_two_paid_margin", math.nan)), paid_margin, rel_tol=0.0, abs_tol=5e-13), consequences.get("cutoff_two_paid_margin"), paid_margin)
    add("consequence_cutoff_two_lower_constant", math.isclose(float(consequences.get("cutoff_two_lower_bound_constant", math.nan)), lower_constant, rel_tol=0.0, abs_tol=5e-12), consequences.get("cutoff_two_lower_bound_constant"), lower_constant)
    add("consequence_gibbs_gap_coefficient", consequences.get("gibbs_gap_coefficient") == "9/10", consequences.get("gibbs_gap_coefficient"), "9/10")
    add("consequence_inherited_bg_moment", consequences.get("inherited_bg_ledger_maximum_required_moment") == 30, consequences.get("inherited_bg_ledger_maximum_required_moment"), 30)
    not_established = manifest.get("claims_not_established", {})
    expected_not_established = {
        "paid_torus_h_n_counterexample",
        "uniform_h_n",
        "exact_h_a_packet_assembly",
        "full_overlap_src",
        "nelson",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    }
    add("claims_not_established_nonempty", bool(not_established), sorted(not_established), "nonempty")
    add("claims_not_established_exact_keys", set(not_established) == expected_not_established, sorted(not_established), sorted(expected_not_established))
    add("claims_not_established_all_false", bool(not_established) and all(value is False for value in not_established.values()), not_established, "all false")

    for label, (authority_manifest, authority_result) in AUTHORITY.items():
        pin = manifest.get("authority", {}).get(label, {})
        add(f"{label}_manifest_exists", authority_manifest.exists(), str(authority_manifest.relative_to(REPO)), "exists")
        add(f"{label}_manifest_path", pin.get("manifest", {}).get("path") == repo_path(authority_manifest), pin.get("manifest", {}).get("path"), repo_path(authority_manifest))
        add(f"{label}_manifest_hash", authority_manifest.exists() and pin.get("manifest", {}).get("sha256") == digest(authority_manifest), pin.get("manifest", {}).get("sha256"), None if not authority_manifest.exists() else digest(authority_manifest))
        add(f"{label}_result_exists", authority_result.exists(), str(authority_result.relative_to(REPO)), "exists")
        add(f"{label}_result_path", pin.get("result", {}).get("path") == repo_path(authority_result), pin.get("result", {}).get("path"), repo_path(authority_result))
        add(f"{label}_result_hash", authority_result.exists() and pin.get("result", {}).get("sha256") == digest(authority_result), pin.get("result", {}).get("sha256"), None if not authority_result.exists() else digest(authority_result))
        try:
            authority_record = load_json(authority_result)
        except Exception:
            authority_record = {}
        expected_authority_schema = {
            "a7_renormalised_energy": "tect/a7-classii-renormalised-energy-integrated-result/1.1",
            "a12_source_square": "tect/a12-classii-source-square-integrated-result/1.0",
            "r081_temporal": "tect/a13-cartan-tail-adapted-near-temporal-integrated/1.0",
            "r087_core": "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-integrated/1.0",
            "r091_coefficient": "tect/a13-projected-cartan-full-frame-temporal-boundary-integrated/1.0",
            "r092_perspective": "tect/a13-normalized-cartan-perspective-covariance-frontier-integrated/1.0",
        }[label]
        add(f"{label}_result_passes", authority_passes(authority_record, expected_authority_schema), [authority_record.get("schema"), authority_record.get("status", authority_record.get("verdict"))], [expected_authority_schema, "exact PASS"])

    a1_pin = manifest.get("numerical_authority", {}).get("a1_production_manifest", {})
    add("a1_manifest_exists", A1_MANIFEST.exists(), str(A1_MANIFEST.relative_to(REPO)), "exists")
    add("a1_manifest_path", a1_pin.get("path") == repo_path(A1_MANIFEST), a1_pin.get("path"), repo_path(A1_MANIFEST))
    add(
        "a1_manifest_hash",
        A1_MANIFEST.exists() and a1_pin.get("sha256") == digest(A1_MANIFEST),
        a1_pin.get("sha256"),
        None if not A1_MANIFEST.exists() else digest(A1_MANIFEST),
    )

    source_entries = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "proof_note": NOTE,
    }
    for label, path in source_entries.items():
        pin = manifest.get("sources", {}).get(label, {})
        add(f"{label}_source_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        add(f"{label}_source_path", pin.get("path") == repo_path(path), pin.get("path"), repo_path(path))
        add(f"{label}_source_hash", path.exists() and pin.get("sha256") == digest(path), pin.get("sha256"), None if not path.exists() else digest(path))
        if label != "proof_note":
            add(f"{label}_source_version", path.exists() and pin.get("version") == source_version(path), pin.get("version"), None if not path.exists() else source_version(path))
        else:
            add("proof_note_source_version", pin.get("version") == "1.0", pin.get("version"), "1.0")

    independent_text = INDEPENDENT.read_text(encoding="utf-8") if INDEPENDENT.exists() else ""
    primary_module = "a13_classii_augmented_perspective_gibbs_gap_information_boundary"
    try:
        independent_tree = ast.parse(independent_text)
    except SyntaxError as error:
        import_violations = [repr(error)]
    else:
        import_violations = []
        for node in ast.walk(independent_tree):
            if isinstance(node, ast.Import):
                import_violations.extend(alias.name for alias in node.names if alias.name == primary_module or alias.name.endswith("." + primary_module))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == primary_module or module.endswith("." + primary_module):
                    import_violations.append(module)
    add("independent_no_primary_import", not import_violations, import_violations, [])

    note_text = NOTE.read_text(encoding="utf-8") if NOTE.exists() else ""
    for index, token in enumerate(NOTE_TOKENS, start=1):
        add(f"note_token_{index}", token in note_text, token if token in note_text else None, token)
    control_chars = [ord(character) for character in note_text if ord(character) < 32 and character not in "\t\n\r"]
    add("note_no_control_chars", not control_chars, control_chars, [])
    bare_qquad = []
    bare_quad = []
    for line_number, line in enumerate(note_text.splitlines(), start=1):
        without_qquad = line.replace("\\qquad", "")
        if "qquad" in without_qquad:
            bare_qquad.append(line_number)
        without_spacing = without_qquad.replace("\\quad", "")
        if re.search(r"(?<![A-Za-z])quad(?![A-Za-z])", without_spacing):
            bare_quad.append(line_number)
    add("note_no_bare_qquad", not bare_qquad, bare_qquad, [])
    add("note_no_bare_quad", not bare_quad, bare_quad, [])
    add("note_no_double_interval_comma", ",," not in note_text, ",," if ",," in note_text else "absent", "absent")
    lower_note = note_text.lower()
    scope_tokens = ("no paid torus h_n counterexample", "cutoff-uniform h_n", "nelson estimate", "sector-a closure")
    add("note_scope_firewall", all(token in lower_note for token in scope_tokens), [token for token in scope_tokens if token not in lower_note], [])

    pdf_pin = manifest.get("proof_pdf", {})
    add("pdf_exists", PDF.exists(), str(PDF.relative_to(REPO)), "exists")
    add("pdf_path", pdf_pin.get("path") == repo_path(PDF), pdf_pin.get("path"), repo_path(PDF))
    add("pdf_version", pdf_pin.get("version") == "1.0", pdf_pin.get("version"), "1.0")
    if PDF.exists():
        reader = PdfReader(str(PDF))
        pdf_pages = len(reader.pages)
        pdf_fields = reader.get_fields() or {}
        trailer_text = str(reader.trailer)
        page_texts = [page.extract_text() or "" for page in reader.pages]
        extracted = "\n".join(page_texts)
        add("pdf_hash", pdf_pin.get("sha256") == digest(PDF), pdf_pin.get("sha256"), digest(PDF))
        add("pdf_pages", pdf_pages == pdf_pin.get("pages") == 12, [pdf_pages, pdf_pin.get("pages")], 12)
        add("pdf_no_blank_pages", all(len(text.strip()) >= 100 for text in page_texts), [len(text.strip()) for text in page_texts], "every page has at least 100 extracted characters")
        add("pdf_size", PDF.stat().st_size == pdf_pin.get("size_bytes"), PDF.stat().st_size, pdf_pin.get("size_bytes"))
        add("pdf_unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
        add("pdf_no_forms", not pdf_fields, sorted(pdf_fields), [])
        add("pdf_no_javascript", "/JavaScript" not in trailer_text and "/JS" not in trailer_text, "absent", "absent")
        add("pdf_no_spacing_debris", "qquad" not in extracted and " quad " not in extracted, [token for token in ("qquad", " quad ") if token in extracted], [])
        add("pdf_no_replacement_glyph", "�" not in extracted, "absent" if "�" not in extracted else "present", "absent")
        add("pdf_form_check", pdf_pin.get("form_check") == "PASS", pdf_pin.get("form_check"), "PASS")
        add("pdf_overfull_zero", pdf_pin.get("overfull_hbox_count") == 0, pdf_pin.get("overfull_hbox_count"), 0)
        add("pdf_visual_qa", pdf_pin.get("visual_qa") == "PASS", pdf_pin.get("visual_qa"), "PASS")
    else:
        for name in ("pdf_hash", "pdf_pages", "pdf_no_blank_pages", "pdf_size", "pdf_unencrypted", "pdf_no_forms", "pdf_no_javascript", "pdf_no_spacing_debris", "pdf_no_replacement_glyph", "pdf_form_check", "pdf_overfull_zero", "pdf_visual_qa"):
            add(name, False, None, "PDF required")

    registry_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    exploration_text = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status_path = CLAIM_DIR / "status.json"
    status_text = status_path.read_text(encoding="utf-8")
    try:
        status_data = load_json(status_path)
    except Exception as error:
        status_data = {}
        add("status_json_load", False, repr(error), "valid JSON")
    else:
        add("status_json_load", True, "valid JSON", "valid JSON")
    surfaces = {
        "gates": REPO / "claims/GATES.md",
        "roadmap": REPO / "ROADMAP.md",
        "changelog": REPO / "CHANGELOG.md",
        "todo": REPO / "TODO.md",
        "sector_readme": REPO / "theory/sector-A-foundation/README.md",
        "main_proof_line": REPO / "theory/main-proof-line.md",
        "theorem_map": REPO / "governance/sector-a-theorem-map.json",
        "lineage": CLAIM_DIR / "LINEAGE.md",
        "claims_ledger": REPO / "CLAIMS.md",
        "proof_evidence_map": REPO / "theory/proof-evidence-map.md",
    }
    surface_text = {label: path.read_text(encoding="utf-8") for label, path in surfaces.items()}
    for token in NEGATIVE_RESULTS:
        heading = f"### {token} --"
        heading_count = registry_text.count(heading)
        section_start = registry_text.find(heading)
        section_end = registry_text.find("\n### ", section_start + len(heading)) if section_start >= 0 else -1
        section = registry_text[section_start : None if section_end < 0 else section_end] if section_start >= 0 else ""
        add(f"registry_{token.lower()}_heading_unique", heading_count == 1, heading_count, 1)
        add(
            f"registry_{token.lower()}_detailed_fields",
            all(field in section for field in ("**Failure mode:**", "**Evidence:**", "**Consequence:**")),
            [field for field in ("**Failure mode:**", "**Evidence:**", "**Consequence:**") if field in section],
            ["**Failure mode:**", "**Evidence:**", "**Consequence:**"],
        )

    exploration_records: list[dict[str, Any]] = []
    exploration_errors: list[str] = []
    for line_number, line in enumerate(exploration_text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            exploration_errors.append(f"line {line_number}: {error}")
        else:
            if isinstance(value, dict):
                exploration_records.append(value)
            else:
                exploration_errors.append(f"line {line_number}: not an object")
    add("exploration_jsonl_valid", not exploration_errors, exploration_errors, [])
    for token in EXPLORATIONS:
        matches = [record for record in exploration_records if record.get("id") == token]
        add(f"exploration_{token.lower()}_unique", len(matches) == 1, len(matches), 1)
        record = matches[0] if len(matches) == 1 else {}
        add(
            f"exploration_{token.lower()}_verdict",
            record.get("verdict") == EXPLORATION_VERDICTS[token],
            record.get("verdict"),
            EXPLORATION_VERDICTS[token],
        )
        formal_refs = record.get("formal_refs", {})
        add(
            f"exploration_{token.lower()}_formal_refs",
            formal_refs.get("results") == ["R-093"]
            and bool(formal_refs.get("negatives"))
            and bool(record.get("evidence_refs"))
            and record.get("claim_ids") == [CLAIM]
            and record.get("task_id") == "T-050",
            {
                "formal_refs": formal_refs,
                "evidence_refs": record.get("evidence_refs"),
                "claim_ids": record.get("claim_ids"),
                "task_id": record.get("task_id"),
            },
            "R-093, a formal negative, evidence, claim, and T-050",
        )

    add("manifest_negative_results_exact", manifest.get("negative_results") == list(NEGATIVE_RESULTS), manifest.get("negative_results"), list(NEGATIVE_RESULTS))
    add("manifest_explorations_exact", manifest.get("explorations") == list(EXPLORATIONS), manifest.get("explorations"), list(EXPLORATIONS))
    add("results_ledger_r093", "R-093" in results_text and RESULT_ID in results_text, "R-093 surface", "R-093 and result ID")
    add("claim_r093", "R-093" in claim_text and "R-093 proves exact augmented and Gibbs-gap" in claim_text, "claim surface", "R-093 boundary")
    add("status_r093", "R-093" in str(status_data.get("statement")) and RESULT_ID in str(status_data.get("notes")), [status_data.get("statement"), status_data.get("notes")], "R-093 and result ID")
    status_reproduction = status_data.get("reproduction", {})
    add("status_reproduction_command", status_reproduction.get("command") == contract.get("command"), status_reproduction.get("command"), contract.get("command"))
    add("status_reproduction_available", status_reproduction.get("status") == "AVAILABLE", status_reproduction.get("status"), "AVAILABLE")
    status_count_tokens = tuple(
        f"{contract.get(key)}/{contract.get(key)}"
        for key in ("primary_assertions", "independent_assertions", "integrated_assertions", "aggregate_assertions")
    )
    add("status_reproduction_counts", all(token in str(status_reproduction.get("expected")) for token in status_count_tokens), status_reproduction.get("expected"), status_count_tokens)
    expected_status_evidence = {
        str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        str(NOTE.relative_to(REPO)).replace("\\", "/"),
        str(PDF.relative_to(REPO)).replace("\\", "/"),
        str(PRIMARY.relative_to(REPO)).replace("\\", "/"),
        str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"),
        str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        str(PRIMARY_RESULT.relative_to(REPO)).replace("\\", "/"),
        str(INDEPENDENT_RESULT.relative_to(REPO)).replace("\\", "/"),
        str(OUTPUT.relative_to(REPO)).replace("\\", "/"),
    }
    actual_status_evidence = set(status_data.get("legacy_evidence", []))
    add("status_r093_evidence", expected_status_evidence <= actual_status_evidence, sorted(expected_status_evidence - actual_status_evidence), [])
    add("status_no_overclaim", all(token in str(status_data.get("no_overclaim")) for token in ("local sign fixture", "not uniform in cutoff", "uniform H_N", "Nelson", "Sector-A")), status_data.get("no_overclaim"), "R-093 scope firewall")
    add("status_next_action", all(token in str(status_data.get("next_action")) for token in ("root-local", "heat", "forest", "2^(j-4k)", "OVERLAP_src")), status_data.get("next_action"), "root-local H_N to OVERLAP_src")
    add("status_last_review", status_data.get("last_review") == "2026-07-27", status_data.get("last_review"), "2026-07-27")
    add("status_tier_and_gates", status_data.get("tier") == "T4" and status_data.get("open_gates") == ["A13-CLASSII-FUTURE-CONTROL-WEIGHTED-INNOVATION-BRACKET", "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION", "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"], [status_data.get("tier"), status_data.get("open_gates")], "T4 and unchanged three gates")
    add("gates_r093", "R-093" in surface_text["gates"] and "root-local" in surface_text["gates"], "gate surface", "R-093 root-local target")
    add("roadmap_r093", "R-093" in surface_text["roadmap"] and "OVERLAP_src" in surface_text["roadmap"], "roadmap surface", "R-093 source-union frontier")
    add("changelog_r093", "R-093 augmented perspective and Gibbs-gap boundary" in surface_text["changelog"], "changelog surface", "R-093 title")
    add("todo_r093", "R-093" in surface_text["todo"] and "root-local" in surface_text["todo"], "TODO surface", "R-093 root-local target")
    add("sector_readme_r093", "R-093" in surface_text["sector_readme"], "sector README surface", "R-093")
    add("main_proof_line_r093", "R-093" in surface_text["main_proof_line"], "main proof line surface", "R-093")
    add("theorem_map_r093", "R-093" in surface_text["theorem_map"], "theorem map surface", "R-093")
    add("lineage_r093", "R-093" in surface_text["lineage"], "lineage surface", "R-093")
    add("claims_ledger_r093", CLAIM in surface_text["claims_ledger"] and "Class-II source, translated model" in surface_text["claims_ledger"], "CLAIMS surface", "A13 claim and title")
    add("proof_map_r093", "R-093" in surface_text["proof_evidence_map"] and "EXP-000191" in surface_text["proof_evidence_map"], "proof map surface", "R-093 and EXP-000191")

    add("run_contract_command", contract.get("command") == "python codes/foundations/a13_classii_augmented_perspective_gibbs_gap_information_boundary_verify.py", contract.get("command"), "canonical command")
    add("primary_schema_contract", contract.get("primary_schema") == "tect/a13-augmented-perspective-gibbs-gap-information-boundary-primary/1.0", contract.get("primary_schema"), "tect/a13-augmented-perspective-gibbs-gap-information-boundary-primary/1.0")
    add("independent_schema_contract", contract.get("independent_schema") == "tect/a13-augmented-perspective-gibbs-gap-information-boundary-independent/1.0", contract.get("independent_schema"), "tect/a13-augmented-perspective-gibbs-gap-information-boundary-independent/1.0")
    add("integrated_schema_contract", contract.get("integrated_schema") == "tect/a13-augmented-perspective-gibbs-gap-information-boundary-integrated/1.0", contract.get("integrated_schema"), "tect/a13-augmented-perspective-gibbs-gap-information-boundary-integrated/1.0")
    add("primary_output_contract", contract.get("primary_output") == str(PRIMARY_RESULT.relative_to(REPO)).replace("\\", "/"), contract.get("primary_output"), str(PRIMARY_RESULT.relative_to(REPO)).replace("\\", "/"))
    add("independent_output_contract", contract.get("independent_output") == str(INDEPENDENT_RESULT.relative_to(REPO)).replace("\\", "/"), contract.get("independent_output"), str(INDEPENDENT_RESULT.relative_to(REPO)).replace("\\", "/"))
    add("integrated_output_contract", contract.get("integrated_output") == str(OUTPUT.relative_to(REPO)).replace("\\", "/"), contract.get("integrated_output"), str(OUTPUT.relative_to(REPO)).replace("\\", "/"))

    integrated_target = len(rows) + 2
    aggregate_target = int(primary.get("assertions_total") or 0) + int(independent.get("assertions_total") or 0) + integrated_target
    if count_only:
        print(f"R-093 integrated assertion candidate: {integrated_target}")
        print(f"R-093 aggregate assertion candidate: {aggregate_target}")
        return 0
    add("integrated_manifest_count", contract.get("integrated_assertions") == integrated_target, contract.get("integrated_assertions"), integrated_target)
    add("aggregate_manifest_count", contract.get("aggregate_assertions") == aggregate_target, contract.get("aggregate_assertions"), aggregate_target)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-augmented-perspective-gibbs-gap-information-boundary-integrated/1.0",
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "aggregate_assertions_passed": int(primary.get("assertions_passed") or 0) + int(independent.get("assertions_passed") or 0) + passed,
        "aggregate_assertions_total": aggregate_target,
        "scope": "Hash-pinned R-093 boundary package; complete uniform H_N, Nelson, measure construction, and Sector A remain open.",
        "assertions": rows,
    }
    atomic_json(OUTPUT, payload)
    print(f"R-093 integrated: {passed}/{len(rows)} assertions {payload['status']}")
    print(f"R-093 aggregate: {payload['aggregate_assertions_passed']}/{payload['aggregate_assertions_total']}")
    print(f"result: {OUTPUT.relative_to(REPO)}")
    if passed != len(rows):
        for row in rows:
            if row["status"] == "FAIL":
                print(f"FAIL {row['name']}: actual={row['actual']!r}, expected={row['expected']!r}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
