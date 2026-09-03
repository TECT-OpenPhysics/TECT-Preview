#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-LT3-RS-v0."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-LT3-RS-v0"
SLUG = "pre-a-cp1-lt3-rs-common-container"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_lt3_rs_common_container.py"
INDEPENDENT = (
    REPO / "codes/foundations/pre_a_cp1_lt3_rs_common_container_independent.py"
)
MANIFEST = REPO / "strategy/pre-a-cp1-lt3-rs-common-container-manifest.json"
NOTE = REPO / "strategy/pre-a-cp1-lt3-rs-common-container-certificate-260803.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
UPSTREAM_NOGO = REPO / "strategy/pre-a-pah1-m2-strict-composition-nogo-manifest.json"
UPSTREAM_PAM2 = REPO / "strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-integrated-{SLUG}/result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT
EXPECTED_PRIMARY_ASSERTIONS = 75
EXPECTED_INDEPENDENT_ASSERTIONS = 64


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted((serial(item) for item in value), key=str)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_child(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )

    required_files = (
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        NOTE,
        STRATEGY_INDEX,
        NEGATIVE_REGISTRY,
        UPSTREAM_NOGO,
        UPSTREAM_PAM2,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    authority_files = (VERIFIER,) + required_files
    for path in required_files:
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "authority",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream_nogo = json.loads(UPSTREAM_NOGO.read_text(encoding="utf-8"))
    upstream_pam2 = json.loads(UPSTREAM_PAM2.read_text(encoding="utf-8"))
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    check(
        "manifest candidate id",
        manifest["candidate_id"] == CANDIDATE_ID,
        manifest["candidate_id"],
        CANDIDATE_ID,
        "identity",
    )
    check(
        "manifest task and contexts",
        (
            manifest["task_id"],
            manifest["claim_context"],
            manifest["comparison_context"],
            manifest["claim_bearing"],
        )
        == ("T-054", CLAIM_CONTEXT, "A2-FULL-PRODUCTION-WELLPOSED", False),
        (
            manifest["task_id"],
            manifest["claim_context"],
            manifest["comparison_context"],
            manifest["claim_bearing"],
        ),
        ("T-054", CLAIM_CONTEXT, "A2-FULL-PRODUCTION-WELLPOSED", False),
        "identity",
    )
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    allowed_standard_roots = {
        "__future__",
        "argparse",
        "cmath",
        "fractions",
        "hashlib",
        "itertools",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
        "typing",
    }
    check(
        "independent route imports only its frozen standard-library set",
        imported_roots == allowed_standard_roots,
        sorted(imported_roots),
        sorted(allowed_standard_roots),
        "independence",
    )

    with tempfile.TemporaryDirectory(prefix="tect-cp1-lt3-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    check(
        "fresh primary equals stored primary",
        canonical(primary) == canonical(stored_primary),
        sha256(STORED_PRIMARY),
        "fresh/stored canonical equality",
        "freshness",
    )
    check(
        "fresh independent equals stored independent",
        canonical(independent) == canonical(stored_independent),
        sha256(STORED_INDEPENDENT),
        "fresh/stored canonical equality",
        "freshness",
    )
    for label, payload in (("primary", primary), ("independent", independent)):
        check(
            f"{label} candidate id",
            payload["candidate_id"] == CANDIDATE_ID,
            payload["candidate_id"],
            CANDIDATE_ID,
            "identity",
        )
        check(
            f"{label} assertions all pass",
            payload["assertions"]["passed"] == payload["assertions"]["total"],
            payload["assertions"]["passed"],
            payload["assertions"]["total"],
            "children",
        )
        check(
            f"{label} identity fields match the manifest",
            (
                payload["candidate_id"],
                payload["candidate_family"],
                payload["version"],
                payload["task_id"],
                payload["claim_context"],
                payload["comparison_context"],
                payload["claim_bearing"],
            )
            == (
                manifest["candidate_id"],
                manifest["candidate_family"],
                manifest["package_version"],
                manifest["task_id"],
                manifest["claim_context"],
                manifest["comparison_context"],
                manifest["claim_bearing"],
            ),
            (
                payload["candidate_id"],
                payload["candidate_family"],
                payload["version"],
                payload["task_id"],
                payload["claim_context"],
                payload["comparison_context"],
                payload["claim_bearing"],
            ),
            "manifest identity tuple",
            "identity",
        )

    primary_row_names = [row["name"] for row in primary["assertions"]["rows"]]
    independent_row_names = [
        row["name"] for row in independent["assertions"]["rows"]
    ]
    check(
        "primary assertion count is frozen and row names are unique",
        len(primary_row_names) == EXPECTED_PRIMARY_ASSERTIONS
        and len(set(primary_row_names)) == EXPECTED_PRIMARY_ASSERTIONS,
        (len(primary_row_names), len(set(primary_row_names))),
        (EXPECTED_PRIMARY_ASSERTIONS, EXPECTED_PRIMARY_ASSERTIONS),
        "children",
    )
    check(
        "independent assertion count is frozen and row names are unique",
        len(independent_row_names) == EXPECTED_INDEPENDENT_ASSERTIONS
        and len(set(independent_row_names)) == EXPECTED_INDEPENDENT_ASSERTIONS,
        (len(independent_row_names), len(set(independent_row_names))),
        (EXPECTED_INDEPENDENT_ASSERTIONS, EXPECTED_INDEPENDENT_ASSERTIONS),
        "children",
    )
    required_primary_rows = {
        "ordered-side pointwise complete square",
        "ordered classical minimum lies strictly below the same-H zero field",
        "differentiating the Hamiltonian dispersion gives the gradient formula",
        "off-node critical gradient formula includes the full speed factor",
        "critical global Lipschitz envelope carries the same speed coefficient",
        "side 4 complement spectral gap",
        "side 8 complement spectral gap",
        "side 12 complement spectral gap",
        "side 4 quarter-shift field attains the exact minimum",
        "side 8 quarter-shift field attains the exact minimum",
        "side 12 quarter-shift field attains the exact minimum",
        "ordered Hessian minus its floor is an exact stencil Gram matrix",
        "a kernel ground vector attains the ordered Hessian floor",
        "side 4 low-energy Fourier concentration bound is executable",
        "side 4 low-energy constant-magnitude bound is executable",
        "ordered-well product-Gaussian Rayleigh density",
        "Gaussian trial has an exact negative rational witness",
        "transitive invariant site subsets are only empty or full",
    }
    required_independent_rows = {
        "same-H ordered minimum is below the zero field",
        "side 4 direct complement gap",
        "side 8 direct complement gap",
        "side 12 direct complement gap",
        "side 4 constructed quarter-shift field attains the exact minimum",
        "side 8 constructed quarter-shift field attains the exact minimum",
        "side 12 constructed quarter-shift field attains the exact minimum",
        "independent omega directional difference derives the full 4c/chi factor",
        "direct ordered Hessian Fourier spectrum has floor minus 2r",
        "direct DFT low-energy Fourier concentration bound",
        "direct field low-energy constant-magnitude bound",
        "independent Gaussian moments reproduce the closed Rayleigh formula",
        "independent Gaussian trial gives an exact negative witness",
        "no proper invariant site subset follows from transitive input",
    }
    check(
        "primary load-bearing assertion rows are present",
        required_primary_rows.issubset(set(primary_row_names)),
        sorted(required_primary_rows - set(primary_row_names)),
        [],
        "children",
    )
    check(
        "independent load-bearing assertion rows are present",
        required_independent_rows.issubset(set(independent_row_names)),
        sorted(required_independent_rows - set(independent_row_names)),
        [],
        "children",
    )

    check(
        "primary exact classical ground count",
        primary["exact_results"]["ground_state_count"] == 256,
        primary["exact_results"]["ground_state_count"],
        256,
        "cross_route",
    )
    check(
        "independent exact classical ground count",
        independent["exact_results"]["ground_count"] == 256,
        independent["exact_results"]["ground_count"],
        256,
        "cross_route",
    )
    check(
        "primary kernel stationary count",
        primary["exact_results"]["kernel_stationary_count"] == 6561,
        primary["exact_results"]["kernel_stationary_count"],
        6561,
        "cross_route",
    )
    check(
        "independent kernel stationary count",
        independent["exact_results"]["kernel_stationary_count"] == 6561,
        independent["exact_results"]["kernel_stationary_count"],
        6561,
        "cross_route",
    )

    for side in ("4", "8", "12"):
        primary_fixture = primary["finite_fixtures"][side]
        independent_fixture = independent["fixture_summary"][side]
        check(
            f"side {side} node counts agree",
            primary_fixture["node_count"] == independent_fixture["node_count"] == 8,
            (primary_fixture["node_count"], independent_fixture["node_count"]),
            (8, 8),
            "cross_route",
        )
        check(
            f"side {side} cubic closure agrees",
            primary_fixture["cubic_node_closure"]
            and independent_fixture["triple_closure"],
            (
                primary_fixture["cubic_node_closure"],
                independent_fixture["triple_closure"],
            ),
            (True, True),
            "cross_route",
        )
        check(
            f"side {side} complement gaps agree across exact and numerical routes",
            math.isclose(
                float(primary_fixture["complement_gap"]),
                float(independent_fixture["gap"]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ),
            (
                primary_fixture["complement_gap"],
                independent_fixture["gap"],
            ),
            "exact/numerical equality within 1e-12",
            "cross_route",
        )

    primary_gaussian = Fraction(
        primary["exact_results"]["gaussian_trial_negative_witness"]
    )
    independent_gaussian = Fraction(
        independent["exact_results"]["gaussian_trial_density_fixture"]
    )
    check(
        "negative Gaussian witness agrees exactly across routes",
        primary_gaussian == independent_gaussian and primary_gaussian < 0,
        (primary_gaussian, independent_gaussian),
        "equal and negative",
        "cross_route",
    )
    check(
        "ordered Hessian floor agrees across routes",
        math.isclose(
            float(independent["exact_results"]["ordered_hessian_floor"]),
            2.0,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        )
        and "floor -2r>0" in primary["exact_results"]["ordered_hessian"],
        (
            independent["exact_results"]["ordered_hessian_floor"],
            primary["exact_results"]["ordered_hessian"],
        ),
        (2.0, "primary formula with floor -2r>0"),
        "cross_route",
    )

    primary_scope = primary["scope"]
    independent_scope = independent["scope"]
    manifest_scope = manifest["scope"]
    check(
        "programme scope is exactly identical across manifest and both routes",
        primary_scope == independent_scope == manifest_scope,
        (primary_scope, independent_scope),
        manifest_scope,
        "scope",
    )
    check(
        "no-overclaim boundary is exactly identical across manifest and both routes",
        primary["no_overclaim"]
        == independent["no_overclaim"]
        == manifest["no_overclaim"],
        (primary["no_overclaim"], independent["no_overclaim"]),
        manifest["no_overclaim"],
        "scope",
    )
    for key, expected in (
        ("finite_lattice_classical_theorem", True),
        ("fixed_N_quantum_ground_selection", True),
        ("same_model_classical_below_zero_field", True),
        ("below_physical_empty_space", False),
        ("thermodynamic_limit", False),
        ("characteristic_boundary", False),
        ("cooling_history", False),
        ("cp1_complete", False),
        ("pre_a_complete", False),
    ):
        check(
            f"primary scope flag: {key}",
            primary_scope[key] is expected,
            primary_scope[key],
            expected,
            "scope",
        )
        check(
            f"manifest scope flag: {key}",
            manifest_scope[key] is expected,
            manifest_scope[key],
            expected,
            "scope",
        )

    clause_audit = manifest["cp1_clause_audit"]
    check(
        "primary CP1 clause audit exactly matches the manifest",
        primary["cp1_audit"] == clause_audit,
        primary["cp1_audit"],
        clause_audit,
        "cp1_contract",
    )
    for key in (
        "one_declared_finite_regulator_family_fixed_N_per_instance",
        "one_phase_space_and_weyl_algebra",
        "one_hamiltonian_formula",
        "one_ground_state_rule_unique_per_fixed_parameter_tuple",
        "exact_classical_interacting_ordering_sector",
    ):
        check(
            f"partial CP1 clause passes: {key}",
            clause_audit[key] is True,
            clause_audit[key],
            True,
            "cp1_contract",
        )
    for key in (
        "same_selected_quantum_state_selects_one_ordered_pattern",
        "characteristic_boundary_map_or_reduction",
        "pah1_boundary_role",
        "one_derived_physical_r_history",
        "cp1_complete",
    ):
        check(
            f"open CP1 clause remains false: {key}",
            clause_audit[key] is False,
            clause_audit[key],
            False,
            "cp1_contract",
        )

    check(
        "negative id is fixed",
        manifest["boundary_selection_no_go"]["negative_id"]
        == "NG-2026-08-03-PRE-A-CP1-TRANSLATION-SYMMETRIC-PROPER-BOUNDARY-SELECTION",
        manifest["boundary_selection_no_go"]["negative_id"],
        "NG-2026-08-03-PRE-A-CP1-TRANSLATION-SYMMETRIC-PROPER-BOUNDARY-SELECTION",
        "routing",
    )
    negative_id = manifest["boundary_selection_no_go"]["negative_id"]
    negative_anchor = negative_id.lower()
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    registry_block_start = (
        f'<a id="{negative_anchor}"></a>\n### {negative_id}'
    )
    check(
        "negative registry has one correctly routed explicit anchor and heading",
        registry_text.count(registry_block_start) == 1,
        registry_text.count(registry_block_start),
        1,
        "routing",
    )
    check(
        "negative registry table routes to the CP1 boundary result",
        f"[{negative_id}](#{negative_anchor})" in registry_text,
        f"[{negative_id}](#{negative_anchor})" in registry_text,
        True,
        "routing",
    )
    strategy_index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    check(
        "strategy index routes the candidate and both authorities",
        CANDIDATE_ID in strategy_index_text
        and MANIFEST.name in strategy_index_text
        and NOTE.name in strategy_index_text,
        (
            CANDIDATE_ID in strategy_index_text,
            MANIFEST.name in strategy_index_text,
            NOTE.name in strategy_index_text,
        ),
        (True, True, True),
        "routing",
    )
    check(
        "upstream strict no-go required a common parent",
        upstream_nogo["scope"]["common_parent_and_energy_ledger_required"] is True,
        upstream_nogo["scope"]["common_parent_and_energy_ledger_required"],
        True,
        "dependency_boundary",
    )
    check(
        "upstream strict no-go did not prove a physical vacuum",
        upstream_nogo["scope"]["physical_vacuum_selected"] is False,
        upstream_nogo["scope"]["physical_vacuum_selected"],
        False,
        "dependency_boundary",
    )
    check(
        "upstream PA-M2 itself forbids physical causal overclaim",
        "does not derive causal structure" in upstream_pam2["no_overclaim"],
        "does not derive causal structure" in upstream_pam2["no_overclaim"],
        True,
        "dependency_boundary",
    )

    energy_ledger = manifest["energy_reference_ledger"]
    check(
        "same-H classical sign is proved",
        energy_ledger["classical_below_zero_field"].startswith("PROVED"),
        energy_ledger["classical_below_zero_field"],
        "PROVED at identical conventions",
        "energy_reference",
    )
    check(
        "physical empty space remains unidentified",
        energy_ledger["physical_empty_space"] == "UNIDENTIFIED",
        energy_ledger["physical_empty_space"],
        "UNIDENTIFIED",
        "energy_reference",
    )
    check(
        "below physical empty space remains untested",
        energy_ledger["below_physical_empty_space"] == "NOT TESTED",
        energy_ledger["below_physical_empty_space"],
        "NOT TESTED",
        "energy_reference",
    )

    note_text = NOTE.read_text(encoding="utf-8")
    normalized_note = " ".join(note_text.replace("`", "").split())
    required_phrases = (
        "first exact same-Hamiltonian answer registered in the current TECT/Pre-A programme",
        "It is not yet a comparison with physical empty space",
        "exactly 256",
        "3Q=-Q modulo the reciprocal lattice",
        "quarter-shift sign field",
        "For every fixed N and fixed parameter tuple",
        "globally Lipschitz",
        "-609/8<0",
        "No proper nonempty site boundary is selected",
        "CP1 complete = false",
        "periodic spatial boundary condition cannot be renamed",
        "infinite-dimensional Hilbert space",
        "External mathematical and physical review is invited",
        "No world-first claim is made",
    )
    for phrase in required_phrases:
        check(
            f"certificate contains required phrase: {phrase}",
            phrase in normalized_note,
            phrase in normalized_note,
            True,
            "scope_prose",
        )
    forbidden_phrases = (
        "CP1 is complete",
        "Pre-A is complete",
        "physical empty space is identified",
        "the speed of light is derived",
        "the event horizon is proved",
        "the quantum phase transition is proved",
    )
    for phrase in forbidden_phrases:
        check(
            f"certificate omits forbidden overclaim: {phrase}",
            phrase not in note_text,
            phrase in note_text,
            False,
            "scope_prose",
        )

    expected_artifacts = {
        "certificate": NOTE,
        "primary_script": PRIMARY,
        "independent_script": INDEPENDENT,
        "integrated_verifier": VERIFIER,
        "primary_result": STORED_PRIMARY,
        "independent_result": STORED_INDEPENDENT,
        "integrated_result": STORED_INTEGRATED,
    }
    for key, path in expected_artifacts.items():
        declared = (REPO / manifest["artifacts"][key]).resolve()
        check(
            f"manifest artifact path: {key}",
            declared == path.resolve(),
            relative(declared),
            relative(path.resolve()),
            "artifact_routing",
        )

    authority_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): sha256(path)
        for path in authority_files
    }
    expected_hash_keys = {
        str(path.relative_to(REPO)).replace("\\", "/") for path in authority_files
    }
    check(
        "authority hash key set is exact and includes the verifier",
        set(authority_hashes) == expected_hash_keys
        and str(VERIFIER.relative_to(REPO)).replace("\\", "/") in authority_hashes,
        sorted(authority_hashes),
        sorted(expected_hash_keys),
        "authority",
    )

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "verdict": "PASS: one local finite-lattice family proves an exact same-H classical ordering reference and supplies a unique ground-state rule per fixed parameter tuple, but CP1 remains incomplete because no characteristic-boundary role, pure ordered quantum phase, physical empty-space reference or r history is derived",
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
            "integrator": len(rows),
            "combined": primary["assertions"]["passed"]
            + independent["assertions"]["passed"]
            + len(rows),
        },
        "authority_hashes": authority_hashes,
        "scope": manifest["scope"],
        "cp1_clause_audit": clause_audit,
        "energy_reference_ledger": energy_ledger,
        "negative_id": manifest["boundary_selection_no_go"]["negative_id"],
        "next_gate": manifest["minimum_repair"]["causal_parent_route"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and STORED_INTEGRATED.is_file():
        stored = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored integrated artifact is stale; regenerate it")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    child = payload["child_assertions"]
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"combined={child['combined']} | {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
