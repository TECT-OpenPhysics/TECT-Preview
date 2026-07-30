#!/usr/bin/env python3
"""Integrated child and contract audit for the scoped A13 R-135 evidence."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"
SCHEMA = "tect/a13-variance-retained-sequential-atom-refinement-boundary-integrated/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_variance_retained_sequential_atom_refinement_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_variance_retained_sequential_atom_refinement_boundary_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-variance-retained-sequential-atom-refinement-boundary/"
    "result.json"
)
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-variance-retained-sequential-atom-refinement-boundary/"
    "result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-variance-retained-sequential-atom-refinement-boundary/"
    "result.json"
)
R087_RESULT = CLAIM_DIR / (
    "runs/2026-07-25-primary-cartan-spatial-decay-rational-trace-"
    "variational-core-reduction/result.json"
)
R088_RESULT = CLAIM_DIR / (
    "runs/2026-07-25-primary-direct-root-cartan-schur-sequential-secant-"
    "rational-conditional-trace/result.json"
)
R125_RESULT = CLAIM_DIR / (
    "runs/2026-07-30-integrated-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)
R134_RESULT = CLAIM_DIR / (
    "runs/2026-07-31-primary-terminal-smoothing-fixed-law-action-"
    "aggregate-collar-boundary/result.json"
)
R125_RESULT_ID = (
    "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-"
    "OPERATOR-BOUNDARY"
)
EXISTING_NEGATIVE = (
    "NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION"
)
SCALED_FIXTURE_NEGATIVE = "NG-2026-07-31-A13-COVARIANCE-ENVELOPE-REBATE-ERASURE"
REFINEMENT_NEGATIVE = "NG-2026-07-31-A13-REFINEMENT-UNIFORM-LAST-BLOCK-ELLIPTICITY"
SHARED_HARDENED_ASSERTIONS = {
    "structure::three_channel_identity",
    "structure::channel_hessian_present",
    "structure::channel_control_derivative_present",
    "structure::channel_root_derivative_present",
    "structure::qj_support_hypothesis_explicit",
    "structure::principal_support_within_qj4",
    "rare_event::integer_qmod_exponent",
    "rare_event::one_active_shell_construction",
    "owner::beta_operator",
    "owner::phi_zero",
    "owner::theta_variance",
    "owner::forest_zero",
    "owner::pcomp",
    "owner::trace_excess_target",
    "owner::nonzero_phi",
    "owner::nonzero_phi_pythagoras",
    "owner::nonzero_phi_trace_excess",
    "owner::nonzero_phi_factor_half",
    "owner::a_squared",
    "owner::be_squared",
    "owner::matched_floor_square_coefficient",
    "owner::surrogate_coefficient_negative",
    "owner::complete_low_retained",
    "owner::production_target_open",
    "refinement::covariance_split",
    "refinement::terminal_min_eigenvalue",
    "refinement::q2_cost",
    "refinement::q4_cost",
    "refinement::d2_cost",
    "refinement::d3_cost",
    "refinement::physical_tail_sequence_oracle",
    "refinement::symbolic_tail_limit",
    "refinement::cost_divergence",
    "refinement::maximal_owner_zero_future_covariance",
}
PRIMARY_REQUIRED_ASSERTIONS = {
    "upstream::r087_pass",
    "upstream::r088_pass",
    "upstream::r125_pass",
    "upstream::r125_result_id",
    "upstream::r134_pass",
    "exponents::aggregate_root_margin",
    "exponents::aggregate_gap_margin",
    "exponents::direct_root_margin",
    "exponents::direct_gap_margin",
    "paths::signed_curvature_cancellation",
    "rare_event::source_budget_exponent",
    "rare_event::sextic_budget_exponent",
    "rare_event::mixed_budget_exponent",
    "rare_event::qmod_exponent",
    "rare_event::current_upstream_growth",
    "rare_event::exact_atom_not_refuted",
    "collar::aggregate_constant_matches_r134",
    "collar::direct_constant_matches_r134",
    "collar::upstream_q_ledger_open",
} | SHARED_HARDENED_ASSERTIONS
INDEPENDENT_REQUIRED_ASSERTIONS = {
    "upstream::r087_pass",
    "upstream::r088_pass",
    "upstream::r125_pass",
    "upstream::r125_result_id",
    "upstream::r134_pass",
    "exponents::aggregate_root_margin",
    "exponents::aggregate_gap_margin",
    "exponents::direct_root_margin",
    "exponents::direct_gap_margin",
    "paths::signed_differences_cancel",
    "rare_event::source_budget",
    "rare_event::sextic_budget",
    "rare_event::mixed_budget",
    "rare_event::qmod_growth",
    "rare_event::upstream_N5",
    "rare_event::no_exact_atom_claim",
    "collar::aggregate_constant",
    "collar::direct_constant",
    "collar::upstream_q_open",
} | SHARED_HARDENED_ASSERTIONS


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "output file missing"
    try:
        payload = load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, f"{type(error).__name__}: {error}"
    if not isinstance(payload, dict):
        return None, f"top-level JSON is {type(payload).__name__}, expected object"
    return payload, None


def recompute_assertion_counts(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("assertions")
    if not isinstance(rows, list):
        return {
            "valid": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "invalid_rows": 1,
        }
    statuses = [row.get("status") if isinstance(row, dict) else None for row in rows]
    invalid = sum(status not in {"PASS", "FAIL"} for status in statuses)
    passed = sum(status == "PASS" for status in statuses)
    failed = sum(status == "FAIL" for status in statuses)
    return {
        "valid": invalid == 0,
        "total": len(rows),
        "passed": passed,
        "failed": failed,
        "invalid_rows": invalid,
    }


def optional_digest(path: Path) -> str | None:
    return digest(path) if path.is_file() else None


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
                "id": identifier,
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )


def run_child(script: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def assertion_ids(payload: dict[str, Any]) -> set[str]:
    return {str(row.get("id", "")) for row in payload.get("assertions", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-output", type=Path, default=DEFAULT_PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=DEFAULT_INDEPENDENT_OUTPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    child_runs: dict[str, dict[str, Any]] = {}
    child_outputs = {
        "primary": arguments.primary_output,
        "independent": arguments.independent_output,
    }
    for label, script, output in (
        ("primary", PRIMARY, arguments.primary_output),
        ("independent", INDEPENDENT, arguments.independent_output),
    ):
        try:
            run = run_child(script, output)
            record = {
                "returncode": run.returncode,
                "stdout": run.stdout[-1000:],
                "stderr": run.stderr[-1000:],
            }
        except (OSError, subprocess.SubprocessError) as error:
            record = {
                "returncode": None,
                "stdout": "",
                "stderr": f"{type(error).__name__}: {error}",
            }
        child_runs[label] = record
        audit.check("children", f"{label}_exit", record["returncode"] == 0, record, 0)
        audit.check("children", f"{label}_output", output.is_file(), output.is_file(), True)

    loaded_children: dict[str, dict[str, Any] | None] = {}
    load_errors: dict[str, str | None] = {}
    for label, output in child_outputs.items():
        payload, error = safe_load_json(output)
        loaded_children[label] = payload
        load_errors[label] = error
        audit.check(
            "children",
            f"{label}_json",
            payload is not None,
            error if error is not None else "valid JSON object",
            "valid JSON object",
        )

    if any(payload is None for payload in loaded_children.values()):
        passed = sum(row["status"] == "PASS" for row in audit.rows)
        available_counts = {
            label: recompute_assertion_counts(payload)
            for label, payload in loaded_children.items()
            if payload is not None
        }
        child_total = sum(int(counts["total"]) for counts in available_counts.values())
        child_passed = sum(int(counts["passed"]) for counts in available_counts.values())
        child_failed = sum(
            int(counts["failed"]) + int(counts["invalid_rows"])
            for counts in available_counts.values()
        )
        failure_payload = {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "FAIL",
            "assertions_total": len(audit.rows),
            "assertions_passed": passed,
            "assertions_failed": len(audit.rows) - passed,
            "assertions": audit.rows,
            "aggregate": {
                "assertions_total": child_total + len(audit.rows),
                "assertions_passed": child_passed + passed,
                "assertions_failed": child_failed + len(audit.rows) - passed,
            },
            "children": {
                label: {
                    "path": str(output),
                    "sha256": optional_digest(output),
                    "load_error": load_errors[label],
                    "run": child_runs[label],
                    "recomputed_counts": available_counts.get(label),
                }
                for label, output in child_outputs.items()
            },
            "source_hashes": {
                "primary": digest(PRIMARY),
                "independent": digest(INDEPENDENT),
                "verifier": digest(Path(__file__)),
            },
            "scope": {
                "scoped_executable_evidence": False,
                "incomplete_child_evidence": True,
                "exact_atom_counterexample": False,
                "full_production_counterexample": False,
                "executable_alone_registers_formal_result": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "At least one child output was missing or unreadable. The verifier "
                "records FAIL and makes no mathematical or production claim."
            ),
        }
        atomic_json(arguments.output, failure_payload)
        print(
            f"R-135 integrated FAIL: {passed}/{len(audit.rows)} "
            "preflight assertions; missing or unreadable child output"
        )
        return 1

    primary = loaded_children["primary"]
    independent = loaded_children["independent"]
    assert primary is not None and independent is not None
    child_counts: dict[str, dict[str, Any]] = {}
    for label, payload, required in (
        ("primary", primary, PRIMARY_REQUIRED_ASSERTIONS),
        ("independent", independent, INDEPENDENT_REQUIRED_ASSERTIONS),
    ):
        counts = recompute_assertion_counts(payload)
        child_counts[label] = counts
        audit.check("children", f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        audit.check("children", f"{label}_claim", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM)
        audit.check("children", f"{label}_result", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID)
        audit.check(
            "children",
            f"{label}_count_consistent",
            counts["valid"]
            and payload.get("assertions_total") == counts["total"]
            and payload.get("assertions_passed") == counts["passed"]
            and payload.get("assertions_failed") == counts["failed"]
            and counts["failed"] == 0,
            {
                "declared": {
                    "total": payload.get("assertions_total"),
                    "passed": payload.get("assertions_passed"),
                    "failed": payload.get("assertions_failed"),
                },
                "recomputed": counts,
            },
            "declared counts equal recomputed all-PASS row counts",
        )
        ids = assertion_ids(payload)
        audit.check("contracts", f"{label}_required_assertions", required <= ids, sorted(required - ids), [])
        scope = payload.get("scope", {})
        for field, expected in (
            ("qmod_majorant_one_use_route_rejected_without_revisits", True),
            ("exact_sequential_atom_counterexample", False),
            ("new_named_negative_result_required", True),
            ("qmod_new_named_negative_result_required", False),
            ("three_channel_formula_contract_checked", True),
            ("qj_support_is_explicit_hypothesis", True),
            ("numerical_full_production_spatial_proof", False),
            ("one_active_shell_no_revisit_is_fixture_input", True),
            ("scaled_r125_fixture_is_full_production_counterexample", False),
            ("full_production_counterexample", False),
            ("r123_full_target_retains_complete_low_owner", True),
            ("r123_trace_excess_is_live_target", True),
            ("production_r123_trace_excess_bound", False),
            ("directed_refinement_last_block_architecture_rejected", True),
            ("physical_tail_covariance_finite_sequence_oracle_checked", True),
            ("physical_tail_covariance_limit_proved_by_finite_oracle", False),
            ("refinement_uniform_terminal_ellipticity", False),
            ("production_one_use_q_ledger", False),
            ("production_near_balanced_headroom", False),
            ("executable_alone_registers_formal_result", False),
            ("sector_a_closed", False),
        ):
            audit.check("scope", f"{label}_{field}", scope.get(field) is expected, scope.get(field), expected)
        audit.check("scope", f"{label}_existing_negative", scope.get("existing_negative_result_reused") == EXISTING_NEGATIVE, scope.get("existing_negative_result_reused"), EXISTING_NEGATIVE)
        audit.check("scope", f"{label}_scaled_fixture_negative", scope.get("scaled_fixture_negative_result") == SCALED_FIXTURE_NEGATIVE, scope.get("scaled_fixture_negative_result"), SCALED_FIXTURE_NEGATIVE)
        audit.check("scope", f"{label}_refinement_negative", scope.get("refinement_negative_result") == REFINEMENT_NEGATIVE, scope.get("refinement_negative_result"), REFINEMENT_NEGATIVE)

    source = INDEPENDENT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    audit.check("independence", "no_sympy", "sympy" not in imports, sorted(imports), "sympy absent")
    audit.check("independence", "no_primary_import_or_read", PRIMARY.name not in source and PRIMARY.stem not in source and RESULT_ID.lower() not in " ".join(imports).lower(), sorted(imports), "primary implementation absent")

    pseq = primary["diagnostics"]["sequential_reparalinearisation"]
    iseq = independent["diagnostics"]["sequential_reparalinearisation"]
    for key in (
        "alpha",
        "beta",
        "safe_c0",
        "q_seq_formula",
        "aggregate_s",
        "aggregate_gamma",
        "aggregate_root_margin",
        "aggregate_gap_margin",
        "direct_s",
        "direct_root_margin",
        "direct_gap_margin",
        "path_weight",
        "three_channels",
        "qj_support_hypothesis",
        "support_relative_radii",
    ):
        audit.check("cross", f"sequential_{key}", str(pseq[key]) == str(iseq[key]), {"primary": pseq[key], "independent": iseq[key]}, "equal")

    prare = primary["diagnostics"]["single_shell_rare_event"]
    irare = independent["diagnostics"]["single_shell_rare_event"]
    for key in (
        "source_budget_exponent",
        "sextic_budget_exponent",
        "mixed_budget_exponent",
        "qmod_exponent",
        "old_weighted_exponent",
        "sample_N",
        "sample_qmod",
        "one_active_shell_profile",
        "revisit_multiplicity",
        "exact_atom_counterexample",
        "existing_negative_result",
        "new_named_negative_result_required",
    ):
        if key in {"sample_N", "sample_qmod"}:
            condition = [int(value) for value in prare[key]] == [
                int(value) for value in irare[key]
            ]
        elif key == "one_active_shell_profile":
            condition = {
                int(offset): int(value) for offset, value in prare[key].items()
            } == {
                int(offset): int(value) for offset, value in irare[key].items()
            }
        else:
            condition = str(prare[key]) == str(irare[key])
        audit.check("cross", f"rare_{key}", condition, {"primary": prare[key], "independent": irare[key]}, "equal")

    powner = primary["diagnostics"]["owner_trace_excess"]
    iowner = independent["diagnostics"]["owner_trace_excess"]
    for key in (
        "p_mass",
        "beta_operator",
        "phi_zero",
        "theta_over_nu_squared",
        "variance_over_nu_squared",
        "pcomp_over_nu_squared",
        "trace_excess_over_nu_squared",
        "fixture_nu",
        "fixture_floor",
        "a_squared",
        "b_e_squared",
        "a_squared_over_nu_squared",
        "b_e_squared_over_e_nu_squared",
        "q_e",
        "forest_minus_q_e",
        "forest_minus_q_e_coefficient",
        "full_target_owners",
        "full_target",
        "production_target_proved",
        "nonzero_phi_fixture",
    ):
        audit.check("cross", f"owner_{key}", str(powner[key]) == str(iowner[key]), {"primary": powner[key], "independent": iowner[key]}, "equal")

    prefine = primary["diagnostics"]["directed_refinement"]
    irefine = independent["diagnostics"]["directed_refinement"]
    for key in (
        "covariance_split",
        "minimum_eigenvalue",
        "q2_cost",
        "q4_cost",
        "d2_cost",
        "d3_cost",
        "maximal_owner_zero_future_covariance",
        "uniform_positive_terminal_ellipticity",
        "full_production_counterexample",
    ):
        audit.check("cross", f"refinement_{key}", str(prefine[key]) == str(irefine[key]), {"primary": prefine[key], "independent": irefine[key]}, "equal")
    common_tail_keys = (
        "epsilon",
        "trace",
        "minimum_eigenvalue",
        "q2_cost",
        "q4_cost",
        "d2_cost",
        "d3_cost",
    )
    primary_tail = [
        {key: str(row[key]) for key in common_tail_keys}
        for row in prefine["tail_table"]
    ]
    independent_tail = [
        {key: str(row[key]) for key in common_tail_keys}
        for row in irefine["tail_table"]
    ]
    audit.check("cross", "refinement_tail_table", primary_tail == independent_tail, {"primary": primary_tail, "independent": independent_tail}, "equal exact tail/cost rows")

    pcollar = primary["diagnostics"]["finite_collar"]
    icollar = independent["diagnostics"]["finite_collar"]
    for key in (
        "aggregate_amplitude_constant",
        "direct_amplitude_constant",
    ):
        audit.check("cross", f"collar_{key}", abs(float(pcollar[key]) - float(icollar[key])) < 2e-15, {"primary": pcollar[key], "independent": icollar[key]}, "within 2e-15")
    for prefix in ("aggregate", "direct"):
        primary_amplitude = float(pcollar[f"{prefix}_amplitude_constant"])
        independent_square = float(icollar[f"{prefix}_square_constant"])
        audit.check(
            "cross",
            f"collar_{prefix}_square_from_primary_amplitude",
            abs(primary_amplitude**2 - independent_square) < 2e-15,
            {
                "primary_exact_square": pcollar[f"{prefix}_square_constant"],
                "primary_amplitude_squared": primary_amplitude**2,
                "independent_square": independent_square,
            },
            "within 2e-15",
        )
    for primary_row, independent_row in zip(pcollar["sample_requirements"], icollar["sample_requirements"]):
        collar = int(primary_row["collar"])
        audit.check("cross", f"collar_sample_{collar}", collar == int(independent_row["collar"]) and abs(float(primary_row["aggregate_required_per_owner_sqrt_q"]) - float(independent_row["aggregate_required_per_owner_sqrt_q"])) < 2e-15 and abs(float(primary_row["direct_required_per_owner_sqrt_q"]) - float(independent_row["direct_required_per_owner_sqrt_q"])) < 2e-15, {"primary": primary_row, "independent": independent_row}, "same collar requirements")
    audit.check("cross", "strict_collar_table", [{k: str(v) for k, v in row.items()} for row in pcollar["strict_collar_table"]] == [{k: str(v) for k, v in row.items()} for row in icollar["strict_collar_table"]], {"primary": pcollar["strict_collar_table"], "independent": icollar["strict_collar_table"]}, "equal")

    r087 = load_json(R087_RESULT)
    r088 = load_json(R088_RESULT)
    r125 = load_json(R125_RESULT)
    r134 = load_json(R134_RESULT)
    audit.check("authority", "r125_path_is_file", R125_RESULT.is_file(), R125_RESULT.relative_to(REPO).as_posix(), "existing R-125 integrated result path")
    audit.check("authority", "r125_pass", r125.get("status") == "PASS", r125.get("status"), "PASS")
    audit.check("authority", "r125_result_id", r125.get("result_id") == R125_RESULT_ID, r125.get("result_id"), R125_RESULT_ID)
    audit.check("authority", "r087_q_formula", r087["cartan"]["conditional_qk"].startswith("C_e*2^{-(6alpha-1)k}"), r087["cartan"]["conditional_qk"], "R-087 q_mod formula")
    audit.check("authority", "r087_q_ledger_open", r087["claims_not_established"]["cartan_one_use_q_ledger"] is False, r087["claims_not_established"]["cartan_one_use_q_ledger"], False)
    audit.check("authority", "r088_N5", r088["direct_cartan"]["old_qmod_direct_growth"] == "N^5", r088["direct_cartan"]["old_qmod_direct_growth"], "N^5")
    audit.check("authority", "r088_exact_bridge_open", r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"] is False, r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"], False)
    audit.check("authority", "r134_q_ledger_open", r134["diagnostics"]["aggregate_shell"]["production_q_ledger"] is False, r134["diagnostics"]["aggregate_shell"]["production_q_ledger"], False)

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(audit.rows) else "FAIL",
        "assertions_total": len(audit.rows),
        "assertions_passed": passed,
        "assertions_failed": len(audit.rows) - passed,
        "assertions": audit.rows,
        "aggregate": {
            "assertions_total": sum(int(counts["total"]) for counts in child_counts.values()) + len(audit.rows),
            "assertions_passed": sum(int(counts["passed"]) for counts in child_counts.values()) + passed,
            "assertions_failed": sum(int(counts["failed"]) + int(counts["invalid_rows"]) for counts in child_counts.values()) + len(audit.rows) - passed,
        },
        "children": {
            "primary": {
                "path": str(arguments.primary_output),
                "sha256": digest(arguments.primary_output),
                "assertions": child_counts["primary"]["total"],
                "recomputed_counts": child_counts["primary"],
            },
            "independent": {
                "path": str(arguments.independent_output),
                "sha256": digest(arguments.independent_output),
                "assertions": child_counts["independent"]["total"],
                "recomputed_counts": child_counts["independent"],
            },
        },
        "source_hashes": {
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "verifier": digest(Path(__file__)),
        },
        "scope": {
            "scoped_executable_evidence": True,
            "sequential_spatial_reparalinearisation_checked": True,
            "three_channel_formula_contract_checked": True,
            "qj_support_is_explicit_hypothesis": True,
            "numerical_full_production_spatial_proof": False,
            "qmod_route_rejected_without_revisit_multiplicity": True,
            "exact_atom_counterexample": False,
            "full_production_counterexample": False,
            "new_named_negative_result_required": True,
            "qmod_new_named_negative_result_required": False,
            "scaled_fixture_negative_result": SCALED_FIXTURE_NEGATIVE,
            "refinement_negative_result": REFINEMENT_NEGATIVE,
            "existing_negative_result_reused": EXISTING_NEGATIVE,
            "r123_full_target_retains_complete_low_owner": True,
            "r123_trace_excess_is_live_target": True,
            "production_r123_trace_excess_bound": False,
            "directed_refinement_last_block_architecture_rejected": True,
            "physical_tail_covariance_finite_sequence_oracle_checked": True,
            "physical_tail_covariance_limit_proved_by_finite_oracle": False,
            "refinement_uniform_terminal_ellipticity": False,
            "conditional_collar_weights_reusable": True,
            "production_q_ledger": False,
            "production_headroom": False,
            "executable_alone_registers_formal_result": False,
            "sector_a_closed": False,
        },
        "no_overclaim": (
            "This integrated audit verifies scoped executable algebra and constants. "
            "The executable alone does not register the result; companion repository "
            "records do. No exact-atom no-go, production q ledger, headroom, or "
            "Sector-A closure is claimed."
        ),
    }
    atomic_json(arguments.output, payload)
    print(
        f"R-135 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} integrated; "
        f"aggregate {payload['aggregate']['assertions_passed']}/"
        f"{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(
                    f"FAIL {row['group']}::{row['name']} "
                    f"actual={row['actual']!r} expected={row['expected']!r}"
                )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
