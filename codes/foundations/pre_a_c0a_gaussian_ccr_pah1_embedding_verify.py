#!/usr/bin/env python3
"""Integrated verifier for PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0."""

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


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0"
SLUG = "pre-a-c0a-gaussian-ccr-pah1-embedding"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_c0a_gaussian_ccr_pah1_embedding.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_c0a_gaussian_ccr_pah1_embedding_independent.py"
MANIFEST = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
NOTE = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-certificate-260803.md"
C0_NOGO_MANIFEST = REPO / "strategy/pre-a-c0-dynamical-completion-underdetermination-manifest.json"
C0A_FINITE_MANIFEST = REPO / "strategy/pre-a-c0a-reflection-positive-transfer-manifest.json"
PAH1_MANIFEST = REPO / "strategy/pre-a-double-null-semilinear-reconstruction-manifest.json"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-c0a-gaussian-ccr-pah1-embedding/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-independent-pre-a-c0a-gaussian-ccr-pah1-embedding/result.json"
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
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
        C0_NOGO_MANIFEST,
        C0A_FINITE_MANIFEST,
        PAH1_MANIFEST,
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
    c0_nogo = json.loads(C0_NOGO_MANIFEST.read_text(encoding="utf-8"))
    finite_c0a = json.loads(C0A_FINITE_MANIFEST.read_text(encoding="utf-8"))
    pah1 = json.loads(PAH1_MANIFEST.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-pa-c0a-gaussian-embedding-") as temporary:
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

    for label, actual in (
        ("primary", primary["candidate_id"]),
        ("independent", independent["candidate_id"]),
        ("manifest", manifest["candidate_id"]),
    ):
        check(
            f"{label} candidate id",
            actual == CANDIDATE_ID,
            actual,
            CANDIDATE_ID,
            "identity",
        )

    exact = primary["exact_results"]
    shared = independent["shared_exact_results"]

    # These are declared exact fixture oracles computed from the inserted
    # Omega=diag(3,5,5) and a=log(2); they are not physical fit parameters.
    cross_oracles = {
        "frequencies": (
            primary["inserted_fixture"]["frequencies"],
            [str(value) for value in shared["frequencies"]],
            manifest["fixture"]["omega"],
            ["3", "5", "5"],
        ),
        "Gaussian covariance": (
            [row[index] for index, row in enumerate(exact["ou_measure_covariance"])],
            shared["covariance"],
            manifest["fixture"]["gaussian_covariance"],
            ["1/6", "1/10", "1/10"],
        ),
        "one-step transfer": (
            [
                primary["inserted_fixture"]["one_particle_transfer"][index][index]
                for index in range(3)
            ],
            shared["transfer"],
            manifest["fixture"]["one_step_transfer"],
            ["1/8", "1/32", "1/32"],
        ),
    }
    for name, (left, middle, declared, oracle) in cross_oracles.items():
        check(
            f"primary-independent-manifest {name}",
            left == middle == declared == oracle,
            (left, middle, declared),
            (oracle, oracle, oracle),
            "cross_implementation",
        )

    check(
        "primary-independent gap",
        "gap=3" in exact["unique_vacuum_and_gap"] and shared["gap"] == 3,
        (exact["unique_vacuum_and_gap"], shared["gap"]),
        ("gap=3", 3),
        "cross_implementation",
    )
    check(
        "primary-independent zero-point shift",
        exact["unnormalised_finite_mode_zero_point_energy"] == "13/2"
        and shared["unnormalised_zero_point_energy"] == "13/2"
        and manifest["normalization_ledger"]["fixture_zero_point_energy"] == "13/2",
        (
            exact["unnormalised_finite_mode_zero_point_energy"],
            shared["unnormalised_zero_point_energy"],
            manifest["normalization_ledger"]["fixture_zero_point_energy"],
        ),
        ("13/2", "13/2", "13/2"),
        "energy_normalization",
    )
    check(
        "primary-independent transfer trace",
        shared["trace_at_log2"] == "8192/6727",
        shared["trace_at_log2"],
        "8192/6727",
        "cross_implementation",
    )

    for label, payload in (("primary", primary), ("independent", independent)):
        assertion_count = payload["assertions"]
        check(
            f"{label} assertions all pass",
            assertion_count["passed"] == assertion_count["total"] > 0,
            assertion_count["passed"],
            assertion_count["total"],
            "execution",
        )

    required_primary_rows = {
        "Mehler noise satisfies the exact semigroup composition law",
        "linear time-reflection Gram fixture factorizes positively",
        "Mehler transfer has no positive uniform lower spectral bound",
        "finite-mode Mehler transfer is trace class despite infinite occupation",
        "Gaussian Schrodinger representation satisfies CCR on the polynomial core",
        "ground-state transform gives the OU generator exactly",
        "finite Fock truncation has the exact top-state commutator anomaly",
        "negative AR1 first chaos violates link reflection positivity",
        "same Gaussian marginal supports distinct reversible OU drifts",
        "massless periodic zero mode destroys the canonical Gaussian covariance",
        "PA-H1 slice reconstruction equals exact KG flow on the embedded range",
        "characteristic embedding preserves the exact symplectic form",
        "characteristic boundary flux equals the exact slice KG energy",
        "finite spectral projector has an off-diagonal nonlocal kernel",
        "generic non-spectral Galerkin embedding is not a dynamical intertwiner",
        "distinct Gaussian extensions agree on the finite image and differ off it",
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
        "independent stationary Mehler covariance",
        "independent Mehler semigroup covariance law",
        "independent transfer eigenvalues descend toward zero",
        "independent trace-class partition sum",
        "independent negative AR1 reflection form",
        "independent same-marginal different-drift control",
        "independent centred-trace boundary symplectic Gram",
        "independent centred-trace boundary energy Gram",
        "independent finite-rank locality counterexample",
        "independent noninvariant Galerkin residual",
    }
    independent_names = {row["name"] for row in independent["assertions"]["rows"]}
    for name in sorted(required_independent_rows):
        check(
            f"independent load-bearing assertion: {name}",
            name in independent_names,
            name in independent_names,
            True,
            "load_bearing_assertions",
        )

    required_scope = {
        "strongly_continuous_gaussian_semigroup": True,
        "full_time_reflection_positivity": True,
        "unbounded_self_adjoint_generator": True,
        "finite_spatial_mode_infinite_occupation_ccr": True,
        "selected_free_benchmark_vacuum_after_omega_is_inserted": True,
        "exact_pah1_finite_image_embedding": True,
        "exact_boundary_slice_symplectic_and_energy_match": True,
        "controlled_smooth_galerkin_covariance_tail": True,
        "finite_fock_truncation_used": False,
        "transfer_uniformly_bounded_below": False,
        "full_continuum_state_limit": False,
        "full_pah1_state_selected": False,
        "hadamard_property_certified": False,
        "spatial_locality_certified": False,
        "causal_cone_derived": False,
        "absolute_or_physical_vacuum_energy_derived": False,
        "empty_space_or_no_condensate_energy_comparison": False,
        "hbar_origin_derived": False,
        "kg_operator_or_dispersion_derived": False,
        "time_order_scale_or_arrow_derived": False,
        "physical_c0_branch_selected": False,
        "gravity_derived": False,
        "event_horizon_identified": False,
        "pa_m2_composition": False,
        "cooling_history_derived": False,
        "pre_a_complete": False,
    }
    for key, expected in required_scope.items():
        actual = manifest["scope"][key]
        check(
            f"manifest scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )

    primary_scope_pairs = {
        "strongly_continuous_gaussian_semigroup": True,
        "generally_unbounded_self_adjoint_generator": True,
        "exact_infinite_occupation_ccr_for_three_spatial_modes": True,
        "exact_pah1_finite_mode_embedding": True,
        "full_continuum_state_limit": False,
        "full_pah1_state_selected": False,
        "hadamard_property_certified": False,
        "absolute_or_physical_vacuum_energy_derived": False,
        "kg_operator_or_dispersion_derived": False,
        "physical_c0_branch_selected": False,
        "pa_m2_composition": False,
        "pre_a_complete": False,
    }
    for key, expected in primary_scope_pairs.items():
        actual = primary["scope"][key]
        check(
            f"primary scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )

    independent_scope_pairs = {
        "finite_spatial_mode_infinite_occupation_semigroup": True,
        "exact_quasi_free_ccr_state": True,
        "exact_pah1_finite_image_embedding": True,
        "full_pah1_state": False,
        "hadamard_limit": False,
        "spatial_locality": False,
        "causal_cone": False,
        "absolute_vacuum_energy": False,
        "hbar_origin": False,
        "kg_dispersion_derived": False,
        "physical_c0_selection": False,
        "pa_m2_composition": False,
        "pre_a_complete": False,
    }
    for key, expected in independent_scope_pairs.items():
        actual = independent["scope"][key]
        check(
            f"independent scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )

    check(
        "static underdetermination remains authoritative",
        c0_nogo["scope"]["pa_m2_static_functional_selects_unique_dynamics"] is False,
        c0_nogo["scope"]["pa_m2_static_functional_selects_unique_dynamics"],
        False,
        "dependency_boundary",
    )
    check(
        "finite C0-A calibration remains nonemergent",
        finite_c0a["scope"]["time_order_and_spacing_inserted"] is True
        and finite_c0a["scope"]["pre_a_complete"] is False,
        (
            finite_c0a["scope"]["time_order_and_spacing_inserted"],
            finite_c0a["scope"]["pre_a_complete"],
        ),
        (True, False),
        "dependency_boundary",
    )
    check(
        "PA-H1 still transports rather than selects a full state",
        pah1["scope"]["linear_algebraic_boundary_state_transport"] is True
        and pah1["scope"]["selected_hadamard_state"] is False
        and pah1["scope"]["pre_a_complete"] is False,
        (
            pah1["scope"]["linear_algebraic_boundary_state_transport"],
            pah1["scope"]["selected_hadamard_state"],
            pah1["scope"]["pre_a_complete"],
        ),
        (True, False, False),
        "dependency_boundary",
    )

    note_text = NOTE.read_text(encoding="utf-8")
    normalized_note_text = " ".join(note_text.split())
    required_phrases = (
        "not bounded below by a positive",
        "0 is not an eigenvalue",
        "time-reflection identity",
        "P_tau T=S_tau",
        "below empty",
        "no-condensate",
        "full PA-H1 algebra",
        "extension is nonunique",
        "spatially nonlocal",
        "not a new TECT",
        "not close C0 or Pre-A",
        "common parent state and energy normalisation",
        "Osterwalder",
        "Nelson",
    )
    for phrase in required_phrases:
        check(
            f"certificate contains required phrase: {phrase}",
            phrase in normalized_note_text,
            phrase in note_text,
            True,
            "scope_prose",
        )
    forbidden_phrases = (
        "world-first theorem",
        "Pre-A is complete",
        "physical vacuum proved",
        "Hadamard state proved",
        "spacetime is derived",
    )
    for phrase in forbidden_phrases:
        check(
            f"certificate omits forbidden overclaim: {phrase}",
            phrase not in note_text,
            phrase in note_text,
            False,
            "scope_prose",
        )

    authority_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): sha256(path)
        for path in authority_files
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "verdict": "PASS: the finite-spatial-mode infinite-occupation Gaussian/CCR reconstruction and exact PA-H1 finite-image state, symplectic, and energy embedding reproduce independently; transfer lower bound, full/Hadamard state, locality, absolute below-reference vacuum energy, time origin, physical C0 selection, gravity, cooling, PA-M2 composition, and Pre-A remain open",
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
        "next_gate": "derive one common parent state, common-reference energy normalization, and controlled r(tau) history that composes PA-H1 with PA-M2 without changing regulator, volume, boundary, or reference conventions",
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and STORED_INTEGRATED.is_file():
        stored_integrated = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        canonical_stored = json.dumps(
            stored_integrated, sort_keys=True, separators=(",", ":"), ensure_ascii=True
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
