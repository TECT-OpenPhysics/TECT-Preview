#!/usr/bin/env python3
"""Integrated authority, PDF, ledger, and public-surface audit for R-131."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-"
    "SHELL-BOUNDARY"
)
LEDGER_ID = "R-131"
SLUG = "owner-complete-physical-response-mixed-gram-shell-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST_SCHEMA = f"tect/a13-{SLUG}-manifest/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / (
    "codes/foundations/a13_classii_owner_complete_physical_response_"
    "mixed_gram_shell_boundary.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_owner_complete_physical_response_"
    "mixed_gram_shell_boundary_independent.py"
)
HELPER = REPO / (
    "codes/foundations/a13_classii_endpoint_trace_excess_shell_"
    "coanalysis_shifted_douglas_boundary_verify.py"
)
HELPER_SHA256 = "bfa4073d6fc08f84bd217e90ee95014dead3ce0be95e762d1b223af851d4c7f8"
PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-owner-complete-physical-response-mixed-"
    "gram-shell-boundary/result.json"
)
INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-owner-complete-physical-response-"
    "mixed-gram-shell-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-owner-complete-physical-response-mixed-"
    "gram-shell-boundary/result.json"
)
MANIFEST = CLAIM_DIR / (
    "classii_owner_complete_physical_response_mixed_gram_"
    "shell_boundary_manifest.json"
)
EXPECTED_AUTHORITY_KEYS = {
    "governance",
    "a1",
    "a8_primary",
    "r103",
    "r103_primary",
    "r120",
    "r121",
    "r123",
    "r124",
    "r124_primary",
    "r128",
    "r129",
    "r129_verifier",
    "r130",
    "r130_primary",
}
EXPECTED_FILE_KEYS = {
    "primary",
    "independent",
    "verifier",
    "note",
    "pdf",
    "primary_result",
    "independent_result",
}
EXPECTED_AUTHORITY_PATHS = {
    "governance": "GOVERNANCE.md",
    "a1": "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "a8_primary": "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/runs/2026-07-20-primary-decoupled-nelson/result.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r103_primary": f"claims/{CLAIM}/runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json",
    "r120": f"claims/{CLAIM}/classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
    "r121": f"claims/{CLAIM}/classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json",
    "r123": f"claims/{CLAIM}/classii_six_row_trace_excess_direct_action_boundary_manifest.json",
    "r124": f"claims/{CLAIM}/classii_stationary_polarized_trace_defect_replica_root_shell_boundary_manifest.json",
    "r124_primary": f"claims/{CLAIM}/runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json",
    "r128": f"claims/{CLAIM}/classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json",
    "r129": f"claims/{CLAIM}/classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json",
    "r129_verifier": "codes/foundations/a13_classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_verify.py",
    "r130": f"claims/{CLAIM}/classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json",
    "r130_primary": f"claims/{CLAIM}/runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-response-boundary/result.json",
}
EXPECTED_FILE_PATHS = {
    "primary": "codes/foundations/a13_classii_owner_complete_physical_response_mixed_gram_shell_boundary.py",
    "independent": "codes/foundations/a13_classii_owner_complete_physical_response_mixed_gram_shell_boundary_independent.py",
    "verifier": "codes/foundations/a13_classii_owner_complete_physical_response_mixed_gram_shell_boundary_verify.py",
    "note": f"claims/{CLAIM}/notes/classii-owner-complete-physical-response-mixed-gram-shell-boundary-260731-v1.0.tex.txt",
    "pdf": f"claims/{CLAIM}/notes/classii-owner-complete-physical-response-mixed-gram-shell-boundary-260731-v1.0.pdf",
    "primary_result": f"claims/{CLAIM}/runs/2026-07-31-primary-owner-complete-physical-response-mixed-gram-shell-boundary/result.json",
    "independent_result": f"claims/{CLAIM}/runs/2026-07-31-independent-owner-complete-physical-response-mixed-gram-shell-boundary/result.json",
}
EXPECTED_CHILD_SHA256 = {
    "primary": "db6cc9c1e8fa5ca0a1e0fd739662cf526dada852663f29f69d75bd8c8be7c658",
    "independent": "45a7170a1343562be97ae8c0b908c7924cbeb6260da4667f88e2236dedef4f37",
}
EXPECTED_COMMAND = (
    "E:\\Dev\\TECT.venv\\Scripts\\python.exe "
    "codes/foundations/a13_classii_owner_complete_physical_response_"
    "mixed_gram_shell_boundary_verify.py"
)
EXPECTED_INTEGRATED_OUTPUT = (
    f"claims/{CLAIM}/runs/2026-07-31-integrated-owner-complete-physical-"
    "response-mixed-gram-shell-boundary/result.json"
)
EXPECTED_NEGATIVES = {
    "NG-2026-07-31-A13-DIAGONAL-GRAM-TO-MIXED-CONDITIONAL-RESPONSE",
    "NG-2026-07-31-A13-BOUNDED-MULTIPLIER-TO-SHELL-DECAY",
    "NG-2026-07-31-A13-FIXED-HEAT-UNIFORM-TRANSVERSALITY",
    "NG-2026-07-31-A13-NATURAL-PHASE-HORIZONTAL-XI-METRIC-IDENTIFICATION",
}
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(483, 496)}
EXPECTED_VERDICTS = {
    "EXP-000483": "advanced",
    "EXP-000484": "advanced",
    "EXP-000485": "advanced",
    "EXP-000486": "failed",
    "EXP-000487": "failed",
    "EXP-000488": "failed",
    "EXP-000489": "advanced",
    "EXP-000490": "inconclusive",
    "EXP-000491": "advanced",
    "EXP-000492": "failed",
    "EXP-000493": "failed",
    "EXP-000494": "inconclusive",
    "EXP-000495": "failed",
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def load_helper() -> Any:
    helper_digest = hashlib.sha256(HELPER.read_bytes()).hexdigest()
    if helper_digest != HELPER_SHA256:
        raise RuntimeError(
            "refusing to execute the R-129 helper before its fixed hash is verified: "
            f"{helper_digest} != {HELPER_SHA256}"
        )
    spec = importlib.util.spec_from_file_location("r129_verify_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned R-129 verifier helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = load_helper()
digest = H.digest
load_json = H.load_json
confined_path = H.confined_path
pdf_security_audit = H.pdf_security_audit
render_pdf = H.render_pdf
normalized = H.normalized


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.identifiers: set[str] = set()

    def check(
        self, group: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        identifier = f"{group}::{name}"
        if identifier in self.identifiers:
            raise ValueError(f"duplicate assertion identifier: {identifier}")
        self.identifiers.add(identifier)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(
        self,
        primary: dict[str, Any],
        independent: dict[str, Any],
        contract_observed: dict[str, Any],
    ) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        child_total = int(primary["assertions_total"]) + int(
            independent["assertions_total"]
        )
        child_passed = int(primary["assertions_passed"]) + int(
            independent["assertions_passed"]
        )
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "aggregate": {
                "assertions_total": child_total + len(self.rows),
                "assertions_passed": child_passed + passed,
                "assertions_failed": child_total + len(self.rows)
                - child_passed
                - passed,
            },
            "contract_observed": contract_observed,
            "scope": {
                "conditional_finite_response_factorization_proved": True,
                "deterministic_current_h2_component_proved": True,
                "mixed_gram_information_no_go_proved": True,
                "bounded_multiplier_shell_decay_no_go_proved": True,
                "conditional_acceptance_simplex_proved": True,
                "stratified_xi_radial_coefficient_bound_proved": True,
                "common_phase_full_tangent_identification_rejected": True,
                "fixed_heat_uniform_transversality_rejected": True,
                "production_owner_complete_form_constructed": False,
                "production_c_mix_c_far_c_bal_proved": False,
                "strict_augmented_gap_and_anchor_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-131 proves a conditional finite-cylinder factorization, "
                "one deterministic current-square H2 component bound, four "
                "scoped no-gos, a conditional acceptance simplex, stratified "
                "Xi radial-coefficient coercivity, and fixed-heat non-"
                "uniformity. It proves no "
                "production owner-complete response, C_mix, C_far, c_bal, "
                "low constants, full-tangent Xi coercivity, matching energy, "
                "anchor, OVERLAP_src, "
                "Nelson estimate, removal, interacting measure, or Sector-A "
                "closure."
            ),
        }


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    if not MANIFEST.is_file():
        print("R-131 integrated BLOCKED: manifest missing")
        return 1
    try:
        preflight_manifest = load_json(MANIFEST)
    except (OSError, ValueError, TypeError) as exc:
        print(f"R-131 integrated BLOCKED: manifest unreadable: {exc}")
        return 1
    preflight_authorities = preflight_manifest.get("authorities", {})
    preflight_files = preflight_manifest.get("files", {})
    authority_paths_ok = (
        set(preflight_authorities) == EXPECTED_AUTHORITY_KEYS
        and all(
            preflight_authorities[name].get("path") == expected
            for name, expected in EXPECTED_AUTHORITY_PATHS.items()
        )
    )
    file_paths_ok = (
        set(preflight_files) == EXPECTED_FILE_KEYS
        and all(
            preflight_files[name].get("path") == expected
            for name, expected in EXPECTED_FILE_PATHS.items()
        )
    )
    if not authority_paths_ok or not file_paths_ok:
        print("R-131 integrated BLOCKED: manifest path contract failed pre-execution")
        return 1
    for name, expected_hash in EXPECTED_CHILD_SHA256.items():
        child_path = REPO / EXPECTED_FILE_PATHS[name]
        declared_hash = str(preflight_files[name].get("sha256", ""))
        actual_hash = digest(child_path) if child_path.is_file() else "missing"
        if declared_hash != expected_hash or actual_hash != expected_hash:
            print(
                "R-131 integrated BLOCKED: refusing to execute an unverified child "
                f"{name}: declared={declared_hash}, actual={actual_hash}, "
                f"expected={expected_hash}"
            )
            return 1

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check(
        "children", "primary_exit", primary_run.returncode == 0, primary_run.returncode, 0
    )
    audit.check(
        "children",
        "independent_exit",
        independent_run.returncode == 0,
        independent_run.returncode,
        0,
    )
    for label, path in (
        ("primary", PRIMARY_OUTPUT),
        ("independent", INDEPENDENT_OUTPUT),
    ):
        audit.check(
            "children", f"{label}_output_exists", path.is_file(), path.is_file(), True
        )
    if not PRIMARY_OUTPUT.is_file() or not INDEPENDENT_OUTPUT.is_file():
        print("R-131 integrated BLOCKED: a child output is missing")
        return 1
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    for label, payload, count, schema_suffix in (
        ("primary", primary, 69, "primary/1.0"),
        ("independent", independent, 61, "independent/1.0"),
    ):
        audit.check(
            "children",
            f"{label}_status",
            payload.get("status") == "PASS",
            payload.get("status"),
            "PASS",
        )
        audit.check(
            "children",
            f"{label}_claim",
            payload.get("claim_id") == CLAIM,
            payload.get("claim_id"),
            CLAIM,
        )
        audit.check(
            "children",
            f"{label}_result",
            payload.get("result_id") == RESULT_ID,
            payload.get("result_id"),
            RESULT_ID,
        )
        expected_schema = f"tect/a13-{SLUG}-{schema_suffix}"
        audit.check(
            "children",
            f"{label}_schema",
            payload.get("schema") == expected_schema,
            payload.get("schema"),
            expected_schema,
        )
        audit.check(
            "children",
            f"{label}_count",
            payload.get("assertions_total") == count,
            payload.get("assertions_total"),
            count,
        )
        audit.check(
            "children",
            f"{label}_passed",
            payload.get("assertions_passed") == count,
            payload.get("assertions_passed"),
            count,
        )
        audit.check(
            "children",
            f"{label}_no_failures",
            payload.get("assertions_failed") == 0,
            payload.get("assertions_failed"),
            0,
        )
        assertion_rows = payload.get("assertions")
        audit.check(
            "children",
            f"{label}_row_count",
            isinstance(assertion_rows, list) and len(assertion_rows) == count,
            len(assertion_rows) if isinstance(assertion_rows, list) else type(assertion_rows).__name__,
            count,
        )
        row_identifiers = [
            (row.get("group"), row.get("name"))
            for row in assertion_rows
            if isinstance(row, dict)
        ] if isinstance(assertion_rows, list) else []
        audit.check(
            "children",
            f"{label}_unique_row_identifiers",
            len(row_identifiers) == count and len(set(row_identifiers)) == count,
            len(set(row_identifiers)),
            count,
        )
        audit.check(
            "children",
            f"{label}_all_rows_pass",
            isinstance(assertion_rows, list)
            and len(assertion_rows) == count
            and all(
                isinstance(row, dict) and row.get("status") == "PASS"
                for row in assertion_rows
            ),
            [
                row.get("name") if isinstance(row, dict) else type(row).__name__
                for row in assertion_rows or []
                if not isinstance(row, dict) or row.get("status") != "PASS"
            ],
            [],
        )

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    independent_tree = ast.parse(independent_source)
    imported_roots: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    audit.check(
        "independence",
        "no_sympy_import",
        "sympy" not in imported_roots,
        sorted(imported_roots),
        "sympy absent",
    )
    audit.check(
        "independence",
        "no_primary_filename",
        PRIMARY.name not in independent_source,
        PRIMARY.name in independent_source,
        False,
    )
    for token in (
        "rational_plus",
        "product_modes",
        "float_matmul",
        "heat_average",
        "lambda_large",
    ):
        audit.check(
            "independence",
            f"fixture_{token}",
            token in independent_source,
            token in independent_source,
            True,
        )

    pd = primary["diagnostics"]
    idg = independent["diagnostics"]
    exact_pairs = (
        ("production_P", pd["production"]["P"], idg["production"]["P"]),
        (
            "production_floor",
            pd["production"]["density_floor"],
            idg["production"]["density_floor"],
        ),
        ("production_c0", pd["production"]["c0"], idg["production"]["c0"]),
        ("production_c1", pd["production"]["c1"], idg["production"]["c1"]),
        (
            "production_alpha",
            pd["production"]["alpha"],
            idg["production"]["alpha"],
        ),
        (
            "production_beta",
            pd["production"]["beta_operator"],
            idg["production"]["beta_operator"],
        ),
        (
            "current_L6",
            pd["deterministic_current_h2"]["L6"],
            idg["deterministic_current_h2"]["L6"],
        ),
        (
            "current_H6",
            pd["deterministic_current_h2"]["H6"],
            idg["deterministic_current_h2"]["H6"],
        ),
        (
            "current_component",
            pd["deterministic_current_h2"]["coefficient_before_embedding"],
            idg["deterministic_current_h2"]["coefficient_before_embedding"],
        ),
        (
            "source_action",
            pd["owner_complete_response"]["source_action_coefficient"],
            idg["response"]["source_action_coefficient"],
        ),
        (
            "source_hessian",
            pd["owner_complete_response"]["source_hessian_coefficient"],
            idg["response"]["source_hessian_coefficient"],
        ),
        (
            "sextic_action",
            pd["owner_complete_response"]["terminal_sextic_action_coefficient"],
            idg["response"]["sextic_action_coefficient"],
        ),
        (
            "shell_coefficient",
            pd["shell_boundary"]["selected_output_shell_coefficient"],
            idg["shell"]["selected_output_shell_coefficient"],
        ),
        (
            "shell_mix_forced",
            pd["shell_boundary"]["forced_C_mix_fixture"],
            idg["shell"]["forced_C_mix"],
        ),
        (
            "shell_far_forced",
            pd["shell_boundary"]["forced_C_far_fixture"],
            idg["shell"]["forced_C_far"],
        ),
        (
            "shell_mix_ratio",
            pd["shell_boundary"]["next_shell_C_mix_growth_ratio"],
            idg["shell"]["next_C_mix_growth_ratio"],
        ),
        (
            "shell_far_ratio",
            pd["shell_boundary"]["next_shell_C_far_growth_ratio"],
            idg["shell"]["next_C_far_growth_ratio"],
        ),
        (
            "cartan_oriented",
            pd["acceptance"]["cartan_oriented_coefficient"],
            idg["acceptance"]["cartan_oriented"],
        ),
    )
    for name, primary_value, independent_value in exact_pairs:
        audit.check(
            "cross_child",
            name,
            primary_value == independent_value,
            independent_value,
            primary_value,
        )
    xi_primary = float(Fraction(pd["xi_transversality"]["small_lambda_coefficient"]))
    xi_independent = float(idg["xi"]["asymptotic_target"])
    audit.check(
        "cross_child",
        "xi_asymptotic",
        math.isclose(xi_primary, xi_independent, rel_tol=2e-12, abs_tol=0.0),
        xi_independent,
        xi_primary,
    )
    heat_primary = float(Fraction(pd["heat_boundary"]["T2_scaled_limit"]))
    heat_independent = float(idg["heat"]["scaled_limit_target"])
    audit.check(
        "cross_child",
        "heat_scaled_limit",
        math.isclose(heat_primary, heat_independent, rel_tol=2e-12, abs_tol=0.0),
        heat_independent,
        heat_primary,
    )
    for label, scope in (
        ("primary", pd["scope"]),
        ("independent", independent["scope"]),
    ):
        for field in (
            "production_C_mix",
            "production_C_far",
            "production_c_bal",
            "absolute_anchor",
            "sector_a_closed",
        ):
            if field in scope:
                audit.check(
                    "child_scope",
                    f"{label}_{field}",
                    scope.get(field) is False,
                    scope.get(field),
                    False,
                )

    audit.check("manifest", "exists", MANIFEST.is_file(), MANIFEST.is_file(), True)
    if not MANIFEST.is_file():
        print("R-131 integrated BLOCKED: manifest missing")
        return 1
    manifest = load_json(MANIFEST)
    verification = manifest.get("verification", {})
    audit.check(
        "manifest",
        "schema",
        manifest.get("schema") == MANIFEST_SCHEMA,
        manifest.get("schema"),
        MANIFEST_SCHEMA,
    )
    audit.check(
        "manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM
    )
    audit.check(
        "manifest",
        "result",
        manifest.get("result_id") == RESULT_ID,
        manifest.get("result_id"),
        RESULT_ID,
    )
    audit.check(
        "manifest",
        "ledger",
        manifest.get("result_ledger_id") == LEDGER_ID,
        manifest.get("result_ledger_id"),
        LEDGER_ID,
    )
    audit.check(
        "manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4"
    )
    audit.check(
        "manifest",
        "evidence_grade",
        manifest.get("evidence_grade") == ["ANALYTIC", "EXACT", "EXECUTED"],
        manifest.get("evidence_grade"),
        ["ANALYTIC", "EXACT", "EXECUTED"],
    )
    audit.check(
        "manifest",
        "proof_incomplete",
        manifest.get("proof_complete") is False,
        manifest.get("proof_complete"),
        False,
    )
    scope = manifest.get("scope", {})
    for field in (
        "production_owner_complete_form_constructed",
        "production_uniform_response_proved",
        "production_c_mix_proved",
        "production_c_far_proved",
        "production_c_bal_proved",
        "low_constants_proved",
        "production_matching_energy_proved",
        "strict_augmented_gap_proved",
        "absolute_anchor_proved",
        "overlap_src_proved",
        "nelson_proved",
        "removals_proved",
        "interacting_measure_proved",
        "sector_a_closed",
        "tier_promoted",
    ):
        audit.check(
            "manifest_scope", field, scope.get(field) is False, scope.get(field), False
        )
    for field in (
        "conditional_finite_response_factorization_proved",
        "deterministic_current_h2_component_proved",
        "diagonal_gram_inference_rejected",
        "bounded_multiplier_shell_inference_rejected",
        "conditional_acceptance_simplex_proved",
        "stratified_xi_radial_coefficient_lower_bound_proved",
        "common_phase_full_tangent_identification_rejected",
        "fixed_heat_uniform_transversality_rejected",
    ):
        audit.check(
            "manifest_scope", field, scope.get(field) is True, scope.get(field), True
        )
    no_overclaim = str(manifest.get("no_overclaim", "")).lower()
    audit.check(
        "manifest",
        "no_overclaim_semantics",
        all(token in no_overclaim for token in ("does not", "production", "nelson", "sector-a")),
        manifest.get("no_overclaim"),
        "explicit production/Nelson/Sector-A boundary",
    )
    audit.check(
        "manifest",
        "negative_set",
        set(manifest.get("negative_results", [])) == EXPECTED_NEGATIVES,
        manifest.get("negative_results", []),
        sorted(EXPECTED_NEGATIVES),
    )
    audit.check(
        "manifest",
        "exploration_set",
        set(manifest.get("exploration_ids", [])) == EXPECTED_EXPLORATIONS,
        manifest.get("exploration_ids", []),
        sorted(EXPECTED_EXPLORATIONS),
    )
    audit.check(
        "manifest",
        "primary_contract",
        verification.get("primary_assertions") == 69,
        verification.get("primary_assertions"),
        69,
    )
    audit.check(
        "manifest",
        "independent_contract",
        verification.get("independent_assertions") == 61,
        verification.get("independent_assertions"),
        61,
    )
    audit.check(
        "manifest",
        "primary_schema",
        verification.get("primary_schema") == primary.get("schema"),
        verification.get("primary_schema"),
        primary.get("schema"),
    )
    audit.check(
        "manifest",
        "independent_schema",
        verification.get("independent_schema") == independent.get("schema"),
        verification.get("independent_schema"),
        independent.get("schema"),
    )
    audit.check(
        "manifest",
        "integrated_schema",
        verification.get("integrated_schema") == SCHEMA,
        verification.get("integrated_schema"),
        SCHEMA,
    )
    audit.check(
        "manifest",
        "command",
        verification.get("command") == EXPECTED_COMMAND,
        verification.get("command"),
        EXPECTED_COMMAND,
    )
    audit.check(
        "manifest",
        "integrated_output",
        verification.get("integrated_output") == EXPECTED_INTEGRATED_OUTPUT,
        verification.get("integrated_output"),
        EXPECTED_INTEGRATED_OUTPUT,
    )

    authorities = manifest.get("authorities", {})
    files = manifest.get("files", {})
    audit.check(
        "manifest",
        "authority_keys",
        set(authorities) == EXPECTED_AUTHORITY_KEYS,
        sorted(authorities),
        sorted(EXPECTED_AUTHORITY_KEYS),
    )
    audit.check(
        "manifest",
        "file_keys",
        set(files) == EXPECTED_FILE_KEYS,
        sorted(files),
        sorted(EXPECTED_FILE_KEYS),
    )
    for name, expected_path in EXPECTED_AUTHORITY_PATHS.items():
        audit.check(
            "manifest_paths",
            f"authority_{name}",
            authorities[name].get("path") == expected_path,
            authorities[name].get("path"),
            expected_path,
        )
    for name, expected_path in EXPECTED_FILE_PATHS.items():
        audit.check(
            "manifest_paths",
            f"file_{name}",
            files[name].get("path") == expected_path,
            files[name].get("path"),
            expected_path,
        )
    for name, expected_hash in EXPECTED_CHILD_SHA256.items():
        audit.check(
            "preexecution_hash",
            name,
            files[name].get("sha256") == expected_hash,
            files[name].get("sha256"),
            expected_hash,
        )
    for name in ("primary", "independent", "verifier"):
        audit.check(
            "manifest_versions",
            name,
            files[name].get("version") == "1.0.0",
            files[name].get("version"),
            "1.0.0",
        )
    audit.check(
        "manifest",
        "declared_authority_keys",
        manifest.get("authority_keys") == list(authorities),
        manifest.get("authority_keys"),
        list(authorities),
    )
    audit.check(
        "manifest",
        "declared_file_keys",
        manifest.get("file_keys") == list(files),
        manifest.get("file_keys"),
        list(files),
    )
    authority_paths = [entry.get("path") for entry in authorities.values()]
    audit.check(
        "manifest",
        "unique_authority_paths",
        len(authority_paths) == len(set(authority_paths)),
        authority_paths,
        "all unique",
    )
    for group, entries in (("authority", authorities), ("files", files)):
        for name, entry in entries.items():
            expected_hash = str(entry.get("sha256", ""))
            audit.check(
                group,
                f"{name}_hash_format",
                SHA256_PATTERN.fullmatch(expected_hash) is not None,
                expected_hash,
                "64 lowercase hex",
            )
            path, confined = confined_path(str(entry.get("path", "")))
            audit.check(group, f"{name}_confined", confined, confined, True)
            audit.check(
                group,
                f"{name}_exists",
                confined and path.is_file(),
                path.is_file(),
                True,
            )
            if confined and path.is_file():
                actual_hash = digest(path)
                audit.check(
                    group,
                    f"{name}_sha256",
                    actual_hash == expected_hash,
                    actual_hash,
                    expected_hash,
                )

    a1_payload = load_json(confined_path(authorities["a1"]["path"])[0])
    audit.check(
        "authority_semantics",
        "a1_schema",
        a1_payload.get("schema") == "tect/a1-production-functional-realisation/1.0",
        a1_payload.get("schema"),
        "tect/a1-production-functional-realisation/1.0",
    )
    a8_payload = load_json(confined_path(authorities["a8_primary"]["path"])[0])
    audit.check(
        "authority_semantics",
        "a8_verdict",
        a8_payload.get("verdict") == "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS",
        a8_payload.get("verdict"),
        "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS",
    )
    for name, expected_result in (
        ("r103_primary", "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE"),
        ("r124_primary", "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY"),
        ("r130_primary", "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-RESPONSE-BOUNDARY"),
    ):
        payload = load_json(confined_path(authorities[name]["path"])[0])
        audit.check(
            "authority_semantics",
            f"{name}_pass",
            payload.get("status") == "PASS",
            payload.get("status"),
            "PASS",
        )
        audit.check(
            "authority_semantics",
            f"{name}_result",
            payload.get("result_id") == expected_result,
            payload.get("result_id"),
            expected_result,
        )

    note_path, note_confined = confined_path(files["note"]["path"])
    pdf_path, pdf_confined = confined_path(files["pdf"]["path"])
    if not note_confined or not pdf_confined or not note_path.is_file() or not pdf_path.is_file():
        print("R-131 integrated BLOCKED: note/PDF path contract invalid")
        return 1
    note_check = subprocess.run(
        [
            sys.executable,
            str(REPO / "verification/scripts/build_note_pdf.py"),
            str(note_path),
            "--no-compile",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    audit.check(
        "note", "form_check_exit", note_check.returncode == 0, note_check.returncode, 0
    )
    audit.check(
        "note",
        "form_check_banner",
        "FORM-CHECK: PASS" in note_check.stdout,
        "FORM-CHECK: PASS" in note_check.stdout,
        True,
    )
    note = note_path.read_text(encoding="utf-8")
    note_norm = normalized(note)
    for index, phrase in enumerate(
        (
            "Purpose and scope",
            "One-use owner ledger",
            "Conditional finite-cylinder response theorem",
            "A floor-uniform deterministic current-square component",
            "Diagonal Gram data do not determine the mixed response",
            "Bounded multipliers do not imply dyadic shell decay",
            "Exact conditional acceptance simplex",
            "Stratified $\\Xi$ transversality",
            "Fixed heat cannot supply a uniform transverse gap",
            "Proof-search evidence map",
            "Devil's-advocate review",
            "Executed evidence and reproduction",
            "Result footer",
            "EXP-000483--EXP-000495",
            "Proof complete: false",
        ),
        start=1,
    ):
        present = normalized(phrase) in note_norm
        audit.check("note", f"phrase_{index:02d}", present, present, True)
    audit.check(
        "note",
        "source_note_hash",
        verification.get("source_note_sha256") == digest(note_path),
        verification.get("source_note_sha256"),
        digest(note_path),
    )

    reader = PdfReader(str(pdf_path))
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    compact_extracted = extracted.replace("\n", "").replace(" ", "")
    fields = reader.get_fields() or {}
    pdf_contract = verification.get("pdf", {})
    audit.check(
        "pdf_contract",
        "path",
        pdf_contract.get("path") == EXPECTED_FILE_PATHS["pdf"],
        pdf_contract.get("path"),
        EXPECTED_FILE_PATHS["pdf"],
    )
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check(
        "pdf",
        "pages",
        len(reader.pages) == pdf_contract.get("pages"),
        len(reader.pages),
        pdf_contract.get("pages"),
    )
    audit.check(
        "pdf",
        "all_pages_nonblank",
        all(len(text.strip()) >= 20 for text in extracted_pages),
        [len(text.strip()) for text in extracted_pages],
        "all >= 20",
    )
    audit.check("pdf", "no_form", not fields, sorted(fields), [])
    audit.check(
        "pdf",
        "claim_id_extracted",
        CLAIM in compact_extracted,
        CLAIM in compact_extracted,
        True,
    )
    audit.check("pdf", "r131_extracted", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    security = pdf_security_audit(reader)
    audit.check(
        "pdf", "safe_open_action", security["safe_open_action"], security["open_action"], "safe"
    )
    audit.check("pdf", "no_unsafe_features", not security["findings"], security["findings"], [])
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)
    audit.check(
        "pdf",
        "size",
        pdf_path.stat().st_size == pdf_contract.get("size_bytes"),
        pdf_path.stat().st_size,
        pdf_contract.get("size_bytes"),
    )
    audit.check(
        "pdf",
        "hash",
        digest(pdf_path) == pdf_contract.get("sha256"),
        digest(pdf_path),
        pdf_contract.get("sha256"),
    )
    visual = pdf_contract.get("visual_qa", {})
    audit.check(
        "pdf", "visual_status", visual.get("status") == "PASS", visual.get("status"), "PASS"
    )
    audit.check(
        "pdf",
        "visual_all_pages",
        visual.get("rendered_pages") == 10 and visual.get("inspected_pages") == 10,
        {
            "rendered": visual.get("rendered_pages"),
            "inspected": visual.get("inspected_pages"),
        },
        {"rendered": 10, "inspected": 10},
    )
    audit.check("pdf", "visual_no_defects", visual.get("defects") == [], visual.get("defects"), [])
    audit.check(
        "pdf",
        "overfull_zero",
        pdf_contract.get("overfull_hbox_count") == 0,
        pdf_contract.get("overfull_hbox_count"),
        0,
    )
    for field in (
        "form_check",
        "javascript_check",
        "unsafe_action_check",
        "widget_check",
        "embedded_file_check",
        "encryption_check",
    ):
        audit.check(
            "pdf_contract", field, pdf_contract.get(field) == "PASS", pdf_contract.get(field), "PASS"
        )

    tmp_parent = REPO / "internal" / "tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r131-pdf-freshness-", dir=tmp_parent) as temporary:
        temporary_root = Path(temporary)
        temporary_note = temporary_root / note_path.name
        temporary_note.write_text(note, encoding="utf-8", newline="\n")
        rebuild = subprocess.run(
            [
                sys.executable,
                str(REPO / "verification/scripts/build_note_pdf.py"),
                str(temporary_note),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        rebuilt_pdf = temporary_note.with_name(
            temporary_note.name.removesuffix(".tex.txt") + ".pdf"
        )
        audit.check(
            "pdf_freshness", "rebuild_exit", rebuild.returncode == 0, rebuild.returncode, 0
        )
        audit.check(
            "pdf_freshness",
            "rebuild_overfull_zero",
            "OVERFULL-HBOX: 0" in (rebuild.stdout or ""),
            "OVERFULL-HBOX: 0" in (rebuild.stdout or ""),
            True,
        )
        audit.check(
            "pdf_freshness",
            "rebuilt_pdf_exists",
            rebuilt_pdf.is_file(),
            rebuilt_pdf.is_file(),
            True,
        )
        if rebuilt_pdf.is_file():
            rebuilt_reader = PdfReader(str(rebuilt_pdf))
            rebuilt_pages = [(page.extract_text() or "") for page in rebuilt_reader.pages]
            audit.check(
                "pdf_freshness",
                "rebuilt_page_count",
                len(rebuilt_pages) == len(extracted_pages),
                len(rebuilt_pages),
                len(extracted_pages),
            )
            audit.check(
                "pdf_freshness",
                "source_to_pdf_text_identity",
                [normalized(text) for text in rebuilt_pages]
                == [normalized(text) for text in extracted_pages],
                [len(normalized(text)) for text in rebuilt_pages],
                [len(normalized(text)) for text in extracted_pages],
            )
            pinned_render = temporary_root / "pinned-render"
            rebuilt_render = temporary_root / "rebuilt-render"
            pinned_render.mkdir()
            rebuilt_render.mkdir()
            pinned_exit, _pinned_log, pinned_hashes = render_pdf(
                pdf_path, pinned_render, "page"
            )
            rebuilt_exit, _rebuilt_log, rebuilt_hashes = render_pdf(
                rebuilt_pdf, rebuilt_render, "page"
            )
            expected_page_hashes = visual.get("page_sha256", [])
            audit.check(
                "pdf_freshness", "pinned_render_exit", pinned_exit == 0, pinned_exit, 0
            )
            audit.check(
                "pdf_freshness", "rebuilt_render_exit", rebuilt_exit == 0, rebuilt_exit, 0
            )
            audit.check(
                "pdf_freshness",
                "pinned_render_count",
                len(pinned_hashes) == 10,
                len(pinned_hashes),
                10,
            )
            audit.check(
                "pdf_freshness",
                "manual_visual_hash_binding",
                pinned_hashes == expected_page_hashes,
                pinned_hashes,
                expected_page_hashes,
            )
            audit.check(
                "pdf_freshness",
                "rebuilt_render_identity",
                rebuilt_hashes == pinned_hashes,
                rebuilt_hashes,
                pinned_hashes,
            )

    explorations: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            explorations[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = explorations.get(identifier)
        audit.check(
            "exploration", f"{identifier}_exists", row is not None, row is not None, True
        )
        if row is None:
            continue
        audit.check(
            "exploration",
            f"{identifier}_claim",
            CLAIM in row.get("claim_ids", []),
            row.get("claim_ids", []),
            CLAIM,
        )
        audit.check(
            "exploration",
            f"{identifier}_task",
            row.get("task_id") == "T-050",
            row.get("task_id"),
            "T-050",
        )
        audit.check(
            "exploration",
            f"{identifier}_verdict",
            row.get("verdict") == EXPECTED_VERDICTS[identifier],
            row.get("verdict"),
            EXPECTED_VERDICTS[identifier],
        )
        audit.check(
            "exploration",
            f"{identifier}_formal_result",
            LEDGER_ID in row.get("formal_refs", {}).get("results", []),
            row.get("formal_refs", {}).get("results", []),
            LEDGER_ID,
        )
        for field in (
            "question",
            "finding",
            "decision_reason",
            "boundary",
            "evidence_refs",
            "next_action",
        ):
            audit.check(
                "exploration",
                f"{identifier}_{field}",
                bool(row.get(field)),
                bool(row.get(field)),
                True,
            )

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in sorted(EXPECTED_NEGATIVES):
        heading = f"### {identifier}"
        audit.check("negatives", identifier, heading in negative_text, heading in negative_text, True)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("surface", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    audit.check(
        "surface",
        "status_statement",
        LEDGER_ID in status.get("statement", ""),
        LEDGER_ID in status.get("statement", ""),
        True,
    )
    audit.check(
        "surface",
        "status_next_action",
        "MIXED-REPLICA" in status.get("next_action", ""),
        status.get("next_action"),
        "mixed-replica successor",
    )
    audit.check(
        "surface",
        "status_no_overclaim",
        "does not" in status.get("no_overclaim", "").lower()
        and "sector-a" in status.get("no_overclaim", "").lower(),
        status.get("no_overclaim"),
        "open-scope statement",
    )

    surface_contracts = (
        ("claim", CLAIM_DIR / "claim.md", (LEDGER_ID, RESULT_ID, "EXP-000483--EXP-000495")),
        (
            "lineage",
            CLAIM_DIR / "lineage-narrative.md",
            (
                "R-131 factors any supplied finite-cylinder owner-complete",
                "natural common-phase-horizontal quotient",
                "mixed-replica sextic transversal response",
            ),
        ),
        ("results_ledger", REPO / "RESULTS-LEDGER.md", (f"## {LEDGER_ID}", RESULT_ID)),
        ("todo", REPO / "todo/todo.json", ("T-050", LEDGER_ID, "mixed-replica")),
        ("changelog_source", REPO / "changelog/log.jsonl", (LEDGER_ID, SLUG)),
        ("changelog_render", REPO / "CHANGELOG.md", (LEDGER_ID, "all-page PDF QA")),
        (
            "claims_render",
            REPO / "CLAIMS.md",
            (
                CLAIM,
                "Class-II source, translated model, balanced coefficient jets, and obstruction boundary",
                "T4",
            ),
        ),
        ("proof_map", REPO / "theory/proof-evidence-map.md", (LEDGER_ID, SLUG, "EXP-000495")),
        ("proof_map_json", REPO / "verification/proof-evidence-map.json", (RESULT_ID, "EXP-000495")),
        ("catalog", REPO / "CATALOG.md", (SLUG,)),
        ("catalog_json", REPO / "verification/catalog.json", (SLUG,)),
    )
    for label, path, phrases in surface_contracts:
        audit.check("surface", f"{label}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            surface_text = path.read_text(encoding="utf-8")
            for index, phrase in enumerate(phrases, start=1):
                audit.check(
                    "surface",
                    f"{label}_phrase_{index}",
                    phrase in surface_text,
                    phrase in surface_text,
                    True,
                )

    changelog_rows = [
        json.loads(line)
        for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching_events = [
        row for row in changelog_rows if "R-131 owner-conditioned" in row.get("header", "")
    ]
    audit.check(
        "surface_semantics",
        "unique_r131_event",
        len(matching_events) == 1,
        len(matching_events),
        1,
    )
    latest_event = matching_events[-1] if matching_events else {}
    audit.check(
        "surface_semantics",
        "latest_event_claim",
        latest_event.get("claim_ids") == [CLAIM],
        latest_event.get("claim_ids"),
        [CLAIM],
    )
    audit.check(
        "surface_semantics",
        "latest_event_manifest",
        MANIFEST.relative_to(REPO).as_posix() in latest_event.get("notes", []),
        latest_event.get("notes"),
        MANIFEST.relative_to(REPO).as_posix(),
    )
    audit.check(
        "surface_semantics",
        "latest_event_verifier",
        Path(__file__).relative_to(REPO).as_posix() in latest_event.get("scripts", []),
        latest_event.get("scripts"),
        Path(__file__).relative_to(REPO).as_posix(),
    )
    audit.check(
        "surface_semantics",
        "latest_event_explorations",
        {"EXP-000486", "EXP-000493", "EXP-000494", "EXP-000495"}.issubset(
            set(latest_event.get("keywords", []))
        ),
        latest_event.get("keywords"),
        ["EXP-000486", "EXP-000493", "EXP-000494", "EXP-000495"],
    )

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    active = theorem_map.get("active_frontier", {})
    audit.check(
        "surface",
        "theorem_map_latest",
        active.get("latest_result_id") == RESULT_ID,
        active.get("latest_result_id"),
        RESULT_ID,
    )
    audit.check(
        "surface",
        "theorem_map_successor",
        "MIXED-REPLICA" in active.get("success_condition", ""),
        active.get("success_condition"),
        "mixed-replica successor",
    )

    precontract_count = len(audit.rows)
    precontract_identifier_hash = hashlib.sha256(
        "\n".join(sorted(audit.identifiers)).encode("utf-8")
    ).hexdigest()
    contract_observed = {
        "integrated_precontract_assertions": precontract_count,
        "integrated_precontract_identifier_sha256": precontract_identifier_hash,
        "integrated_assertions": precontract_count + 4,
        "aggregate_assertions": 69 + 61 + precontract_count + 4,
    }
    audit.check(
        "contract",
        "precontract_assertion_count",
        precontract_count
        == int(verification.get("integrated_precontract_assertions", -1)),
        precontract_count,
        verification.get("integrated_precontract_assertions"),
    )
    audit.check(
        "contract",
        "precontract_identifier_hash",
        precontract_identifier_hash
        == verification.get("integrated_precontract_identifier_sha256"),
        precontract_identifier_hash,
        verification.get("integrated_precontract_identifier_sha256"),
    )
    audit.check(
        "contract",
        "integrated_assertion_count",
        len(audit.rows) + 2 == int(verification.get("integrated_assertions", -1)),
        len(audit.rows) + 2,
        verification.get("integrated_assertions"),
    )
    audit.check(
        "contract",
        "aggregate_assertion_count",
        69 + 61 + len(audit.rows) + 1
        == int(verification.get("aggregate_assertions", -1)),
        69 + 61 + len(audit.rows) + 1,
        verification.get("aggregate_assertions"),
    )

    payload = audit.finish(primary, independent, contract_observed)
    atomic_json(arguments.output, payload)
    print(
        f"R-131 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} integrated; "
        f"aggregate {payload['aggregate']['assertions_passed']}/"
        f"{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(
                    f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} "
                    f"expected={row['expected']!r}"
                )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
