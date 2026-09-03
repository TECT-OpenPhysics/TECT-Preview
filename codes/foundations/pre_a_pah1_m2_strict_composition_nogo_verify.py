#!/usr/bin/env python3
"""Integrated verifier for PA-H1-M2-STRICT-COMPOSITION-NOGO-v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-H1-M2-STRICT-COMPOSITION-NOGO-v0"
SLUG = "pre-a-pah1-m2-strict-composition-nogo"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_pah1_m2_strict_composition_nogo.py"
INDEPENDENT = (
    REPO / "codes/foundations/pre_a_pah1_m2_strict_composition_nogo_independent.py"
)
MANIFEST = REPO / "strategy/pre-a-pah1-m2-strict-composition-nogo-manifest.json"
NOTE = REPO / "strategy/pre-a-pah1-m2-strict-composition-nogo-certificate-260803.md"
GAUSSIAN_MANIFEST = (
    REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
)
GAUSSIAN_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-c0a-gaussian-ccr-pah1-embedding/result.json"
)
PAM2_MANIFEST = REPO / "strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json"
PAM2_RESULT = (
    REPO
    / "claims/A2-FULL-PRODUCTION-WELLPOSED/runs"
    / "2026-08-03-primary-pre-a-pa-m2-ci8-rs-dual-lane/result.json"
)
STATIC_DYNAMICS_MANIFEST = (
    REPO / "strategy/pre-a-c0-dynamical-completion-underdetermination-manifest.json"
)
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
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-integrated-{SLUG}"
    / "result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
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
                "actual": actual,
                "expected": expected,
                "group": group,
            }
        )

    required_files = (
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        NOTE,
        GAUSSIAN_MANIFEST,
        GAUSSIAN_RESULT,
        PAM2_MANIFEST,
        PAM2_RESULT,
        STATIC_DYNAMICS_MANIFEST,
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
    gaussian_manifest = json.loads(GAUSSIAN_MANIFEST.read_text(encoding="utf-8"))
    gaussian_result = json.loads(GAUSSIAN_RESULT.read_text(encoding="utf-8"))
    pam2_manifest = json.loads(PAM2_MANIFEST.read_text(encoding="utf-8"))
    pam2_result = json.loads(PAM2_RESULT.read_text(encoding="utf-8"))
    static_manifest = json.loads(STATIC_DYNAMICS_MANIFEST.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-pah1-m2-composition-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))
    for label, stored, fresh in (
        ("primary", stored_primary, primary),
        ("independent", stored_independent, independent),
    ):
        check(
            f"stored {label} artifact equals fresh child output",
            stored == fresh,
            stored == fresh,
            True,
            "stored_artifact_integrity",
        )

    identities = (
        ("primary", primary["candidate_id"], CANDIDATE_ID),
        ("independent", independent["candidate_id"], CANDIDATE_ID),
        ("manifest", manifest["candidate_id"], CANDIDATE_ID),
        (
            "Gaussian dependency",
            gaussian_manifest["candidate_id"],
            "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
        ),
        ("PA-M2 dependency", pam2_manifest["candidate_id"], "PA-M2-CI8-RS-v0"),
        (
            "static-dynamics dependency",
            static_manifest["candidate_id"],
            "PA-C0-DYNAMICAL-COMPLETION-NOGO-v0",
        ),
    )
    for label, actual, expected in identities:
        check(
            f"{label} candidate id",
            actual == expected,
            actual,
            expected,
            "identity",
        )

    primary_fixture = primary["imported_fixture"]
    independent_exact = independent["shared_exact_results"]
    manifest_fixture = manifest["fixture"]
    fixture_oracles = {
        "PA-H1 frequencies": (
            [int(value) for value in primary_fixture["pah1_frequencies"]],
            independent_exact["pah1_frequencies"],
            manifest_fixture["pah1_frequencies"],
            [3, 5, 5],
        ),
        "PA-H1 configuration dimension": (
            primary_fixture["pah1_configuration_dimension"],
            independent_exact["pah1_configuration_dimension"],
            manifest_fixture["pah1_configuration_dimension"],
            3,
        ),
        "PA-H1 phase dimension": (
            primary_fixture["pah1_phase_dimension"],
            independent_exact["pah1_phase_dimension"],
            manifest_fixture["pah1_phase_dimension"],
            6,
        ),
        "PA-M2 configuration dimension": (
            primary_fixture["pam2_configuration_dimension"],
            independent_exact["pam2_configuration_dimension"],
            manifest_fixture["pam2_configuration_dimension"],
            8,
        ),
        "PA-M2 phase dimension": (
            primary_fixture["pam2_phase_dimension"],
            independent_exact["pam2_phase_dimension"],
            manifest_fixture["pam2_phase_dimension"],
            16,
        ),
        "symplectic complement dimension": (
            primary_fixture["symplectic_complement_dimension"],
            independent_exact["symplectic_complement_dimension"],
            manifest_fixture["symplectic_complement_dimension"],
            10,
        ),
    }
    for name, values in fixture_oracles.items():
        left, middle, declared, oracle = values
        check(
            f"primary-independent-manifest {name}",
            left == middle == declared == oracle,
            (left, middle, declared),
            (oracle, oracle, oracle),
            "cross_implementation",
        )

    upstream_gaussian_frequencies = [
        int(value) for value in gaussian_manifest["fixture"]["omega"]
    ]
    check(
        "local PA-H1 frequencies are bound to the upstream Gaussian authority",
        [int(value) for value in primary_fixture["pah1_frequencies"]]
        == independent_exact["pah1_frequencies"]
        == manifest_fixture["pah1_frequencies"]
        == upstream_gaussian_frequencies,
        (
            primary_fixture["pah1_frequencies"],
            independent_exact["pah1_frequencies"],
            manifest_fixture["pah1_frequencies"],
            upstream_gaussian_frequencies,
        ),
        ([3, 5, 5], [3, 5, 5], [3, 5, 5], [3, 5, 5]),
        "dependency_boundary",
    )

    primary_exact = primary["exact_results"]
    manifest_oracles = manifest["exact_oracles"]
    polynomial_oracles = (
        (
            "PA-H1 characteristic polynomial",
            primary_exact["pah1_characteristic_polynomial"],
            independent_exact["pah1_characteristic_polynomial"],
            manifest_oracles["pah1_characteristic_polynomial"],
        ),
        (
            "PA-M2 characteristic polynomial",
            primary_exact["pam2_zero_characteristic_polynomial"],
            independent_exact["pam2_zero_characteristic_polynomial"],
            manifest_oracles["pam2_zero_characteristic_polynomial"],
        ),
    )
    polynomial_s = sp.symbols("s", real=True)
    polynomial_r = sp.symbols("r", real=True)
    polynomial_chi = sp.symbols("chi", positive=True)
    polynomial_locals = {
        "s": polynomial_s,
        "r": polynomial_r,
        "chi": polynomial_chi,
    }
    for name, left, middle, declared in polynomial_oracles:
        expressions = tuple(
            sp.sympify(value.replace("^", "**"), locals=polynomial_locals)
            for value in (left, middle, declared)
        )
        check(
            f"primary-independent-manifest {name}",
            sp.simplify(expressions[0] - expressions[1]) == 0
            and sp.simplify(expressions[0] - expressions[2]) == 0,
            [str(value) for value in expressions],
            "algebraically equal",
            "cross_implementation",
        )

    exact_oracles = {
        "common full frequency ratio": (
            primary_exact["common_full_frequency_ratio"],
            independent_exact["common_full_frequency_ratio"],
            manifest_oracles["common_full_frequency_ratio"],
            None,
        ),
        "cubic third-harmonic cosine coefficient": (
            primary_exact["cubic_third_harmonic_cosine_coefficient"],
            independent_exact["cubic_third_harmonic_cosine_coefficient"],
            manifest_oracles["cubic_third_harmonic_cosine_coefficient"],
            "1/4",
        ),
        "cubic leakage norm squared": (
            primary_exact["cubic_leakage_norm_squared"],
            independent_exact["cubic_leakage_norm_squared"],
            manifest_oracles["cubic_leakage_norm_squared"],
            "1/32",
        ),
        "raw PA-H1 zero point": (
            primary_exact["raw_pah1_zero_point"],
            independent_exact["raw_pah1_zero_point"],
            manifest_oracles["raw_pah1_zero_point"],
            "13/2",
        ),
        "normal-ordered PA-H1 zero point": (
            str(primary_exact["normal_ordered_pah1_zero_point"]),
            str(independent_exact["normal_ordered_pah1_zero_point"]),
            str(manifest_oracles["normal_ordered_pah1_zero_point"]),
            "0",
        ),
        "period": (
            primary_exact["period"],
            independent_exact["period"],
            manifest_oracles["period"],
            "2*pi",
        ),
        "product phase dimension": (
            primary_exact["product_phase_dimension"],
            independent_exact["product_phase_dimension"],
            manifest_oracles["product_phase_dimension"],
            22,
        ),
    }
    for name, values in exact_oracles.items():
        left, middle, declared, oracle = values
        check(
            f"primary-independent-manifest {name}",
            left == middle == declared == oracle,
            (left, middle, declared),
            (oracle, oracle, oracle),
            "cross_implementation",
        )

    c_symbol, chi_symbol = sp.symbols("c chi", positive=True)
    symbolic_locals = {"c": c_symbol, "chi": chi_symbol, "sqrt": sp.sqrt}
    uv_expressions = tuple(
        sp.sympify(value, locals=symbolic_locals)
        for value in (
            primary_exact["pam2_uv_speed_growth_coefficient"],
            independent_exact["pam2_uv_speed_growth_coefficient"],
            manifest_oracles["pam2_uv_speed_growth_coefficient"],
        )
    )
    uv_oracle = 2 * sp.sqrt(c_symbol / chi_symbol)
    check(
        "primary-independent-manifest PA-M2 UV speed coefficient",
        all(sp.simplify(value - uv_oracle) == 0 for value in uv_expressions),
        [str(value) for value in uv_expressions],
        str(uv_oracle),
        "cross_implementation",
    )

    for label, payload in (("primary", primary), ("independent", independent)):
        assertions = payload["assertions"]
        check(
            f"{label} assertions all pass",
            assertions["passed"] == assertions["total"] > 0,
            assertions["passed"],
            assertions["total"],
            "execution",
        )

    required_primary_rows = {
        "strict-interface phase-dimension deficit",
        "explicit rank-six symplectic injection exists",
        "ten-dimensional symplectic complement is explicit",
        "the two positive Gaussian extensions differ on the complement",
        "CI8 real Fourier coordinate map is injective",
        "CI8 quartic integral has an exact Parseval sum-of-squares certificate",
        "interacting target energy has a nonzero fourth-degree coefficient",
        "affine translation does not remove the leading quartic coefficient",
        "a derivative with zero PA-M2 field component is isotropic",
        "PA-H1 characteristic polynomial",
        "PA-M2 zero-background CI8 characteristic polynomial",
        "no single PA-M2 ratio matches both PA-H1 frequency sectors",
        "constant time rescaling cannot remove the frequency-ratio mismatch",
        "the cubic third harmonic lies outside CI8",
        "CI8 projection omits a nonzero cubic-force norm",
        "independent additive shifts can reverse a cross-model energy ordering",
        "PA-H1 finite fixture has period two pi",
        "selected Gaussian covariance is invariant under the full flow",
        "nonvacuum coherent control can vary and cross on a finite interval",
        "PA-M2 group-speed growth coefficient is nonzero",
        "a decoupled product parent is a valid symplectic control",
    }
    primary_names = {row["name"] for row in primary["assertions"]["rows"]}
    for name in sorted(required_primary_rows):
        check(
            f"primary load-bearing assertion: {name}",
            name in primary_names,
            name in primary_names,
            True,
            "load_bearing_assertions",
        )

    required_independent_rows = {
        "independent phase-space deficit",
        "independent no-bijection dimension test",
        "independent explicit symplectic injection pullback",
        "independent full covariances differ off image",
        "independent complement quasi-free mode blocks are positive semidefinite",
        "independent CI8 real Fourier map has identity Gram matrix",
        "independent squared-field zero mode is the coefficient norm",
        "independent quartic integral is the Parseval sum for the squared field",
        "independent affine quartic leading coefficient",
        "independent zero-field derivative is isotropic",
        "independent scalar PA-M2 linearization cannot match two squares",
        "independent frequency-three sector has a matching control",
        "independent frequency-five sector has a matching control",
        "independent triple carrier leaves CI8",
        "independent projected cubic leakage norm",
        "independent additive offset reverses cross-model sign",
        "independent invariant-state history is constant",
        "independent nonvacuum oscillatory crossing remains possible",
        "independent PA-M2 ultraviolet speed coefficient",
        "independent decoupled product dimension",
    }
    independent_names = {
        row["name"] for row in independent["assertions"]["rows"]
    }
    for name in sorted(required_independent_rows):
        check(
            f"independent load-bearing assertion: {name}",
            name in independent_names,
            name in independent_names,
            True,
            "load_bearing_assertions",
        )

    expected_scope = {
        "exact_phase_dimension_mismatch": True,
        "explicit_linear_symplectic_injection": True,
        "linear_symplectic_bijection": False,
        "abstract_cstar_algebra_isomorphism_excluded": False,
        "finite_image_selects_full_pam2_state": False,
        "affine_all_amplitude_interacting_energy_embedding": False,
        "zero_background_full_gaussian_flow_intertwiner": False,
        "zero_fixing_c1_local_flow_embedding": False,
        "ordered_background_flow_embedding_excluded": False,
        "ci8_invariant_under_unchanged_cubic_force": False,
        "projected_ci8_equals_unprojected_dynamics": False,
        "common_absolute_energy_reference": False,
        "below_empty_space_or_no_condensate_comparison": False,
        "stationary_vacuum_generates_nonconstant_r": False,
        "all_nonvacuum_finite_interval_zero_crossings_excluded": False,
        "global_monotone_state_local_cooling_from_periodic_fixture": False,
        "node_local_tree_level_z1_cone_excluded": False,
        "global_unchanged_lorentz_cone_match": False,
        "finite_cutoff_superluminal_signalling_proved": False,
        "unchanged_strict_composition": False,
        "arbitrary_nonlinear_or_holographic_map_excluded": False,
        "larger_common_parent_excluded": False,
        "external_or_dynamic_control_excluded": False,
        "existing_pah1_result_invalidated": False,
        "existing_pam2_result_invalidated": False,
        "common_parent_and_energy_ledger_required": True,
        "physical_vacuum_selected": False,
        "pre_a_complete": False,
    }
    for key, expected in expected_scope.items():
        actual = manifest["scope"][key]
        check(
            f"manifest scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )
        check(
            f"primary scope agrees: {key}",
            primary["scope"][key] is expected,
            primary["scope"][key],
            expected,
            "scope",
        )

    independent_scope = {
        "strict_unchanged_interface_rejected": True,
        "linear_symplectic_injection_exists": True,
        "linear_symplectic_bijection_exists": False,
        "full_state_extension_unique": False,
        "affine_global_interacting_energy_match": False,
        "zero_background_full_flow_intertwiner": False,
        "ci8_nonlinear_invariant_subspace": False,
        "common_energy_zero_identified": False,
        "stationary_vacuum_nonconstant_control": False,
        "nonvacuum_crossing_excluded": False,
        "global_lorentz_cone_match": False,
        "larger_or_nonlinear_parent_excluded": False,
        "pre_a_complete": False,
    }
    for key, expected in independent_scope.items():
        actual = independent["scope"][key]
        check(
            f"independent scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )

    dependency_checks = (
        (
            "Gaussian upstream leaves PA-M2 composition open",
            gaussian_manifest["scope"]["pa_m2_composition"] is False,
        ),
        (
            "Gaussian upstream has no empty-space comparison",
            gaussian_manifest["scope"]["empty_space_or_no_condensate_energy_comparison"]
            is False,
        ),
        (
            "Gaussian result imports the raw thirteen-halves offset",
            gaussian_result["exact_results"][
                "unnormalised_finite_mode_zero_point_energy"
            ]
            == "13/2",
        ),
        (
            "PA-M2 upstream declares composition open",
            pam2_manifest["scope"]["lane_h_to_pa_m2_composition"] is False,
        ),
        (
            "PA-M2 upstream has eight real soft coordinates",
            pam2_result["exact_results"]["physical_soft_coordinates_before_interactions"]
            == 8,
        ),
        (
            "static-dynamics upstream denies a global PA-M2 causal cone",
            static_manifest["scope"]["pa_m2_global_causal_cone"] is False,
        ),
    )
    for name, condition in dependency_checks:
        check(name, condition, condition, True, "dependency_boundary")

    note_text = NOTE.read_text(encoding="utf-8")
    normalized_note = " ".join(note_text.replace("`", "").split())
    required_phrases = (
        "No below-empty-space or no-condensate comparison has been performed",
        "symplectic injection exists",
        "ten-dimensional symplectic complement",
        "Full-state extension is therefore nonunique",
        "no affine symplectic injection",
        "constant time rescaling",
        "3Q is not a CI8 node",
        "1/32",
        "independent additive constants",
        "2*pi periodic flow",
        "nonvacuum coherent observable",
        "unchanged global principal symbols",
        "not a no-go for a larger common parent",
        "common finite-regulator three-torus (T^3) parent",
        "does not prove Pre-A",
        "standard mathematics",
        "not new TECT discoveries",
        "External mathematical and physical review is invited",
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
        "Pre-A is complete",
        "physical vacuum is proved",
        "energy below empty space is proved",
        "all nonlinear maps are excluded",
        "superluminal signalling is proved",
        "PA-H1 and PA-M2 are invalid",
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
        declared_relative = manifest["artifacts"][key]
        expected_relative = str(path.relative_to(REPO)).replace("\\", "/")
        declared = (REPO / declared_relative).resolve()
        check(
            f"manifest artifact path: {key}",
            declared == path.resolve(),
            declared_relative,
            expected_relative,
            "artifact_routing",
        )

    authority_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): sha256(path)
        for path in authority_files
    }
    expected_hash_keys = {
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in authority_files
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
        "verdict": "PASS: the strict unchanged PA-H1/PA-M2 interface is rejected by separately scoped dimension/state, all-amplitude affine energy, zero-background dynamics, and CI8 closure obstructions; common energy zero, monotone vacuum cooling, and global causal matching are not supplied",
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
        "next_gate": manifest["repair_contract"]["CP1"],
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
        canonical_stored = json.dumps(
            stored, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        canonical_fresh = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        if canonical_stored != canonical_fresh:
            raise AssertionError(
                "stored integrated artifact is stale; regenerate without --self-test"
            )
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
