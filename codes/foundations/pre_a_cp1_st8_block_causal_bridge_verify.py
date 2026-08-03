#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-ST8-CB-v0."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-ST8-CB-v0"
PARENT_ID = "PA-CP1-LT3-RS-v0"
CANDIDATE_FAMILY = "PRE-A-STAGGERED-BLOCK-CAUSAL-BRIDGE"
SLUG = "pre-a-cp1-st8-block-causal-bridge"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_block_causal_bridge.py"
INDEPENDENT = (
    REPO / "codes/foundations/pre_a_cp1_st8_block_causal_bridge_independent.py"
)
MANIFEST = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
NOTE = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-certificate-260803.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
UPSTREAM_LT3 = REPO / "strategy/pre-a-cp1-lt3-rs-common-container-manifest.json"
UPSTREAM_LT3_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-lt3-rs-common-container/result.json"
)
UPSTREAM_PAH1 = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
UPSTREAM_PAH1_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-c0a-gaussian-ccr-pah1-embedding/result.json"
)
UPSTREAM_DOUBLE_NULL = (
    REPO / "strategy/pre-a-double-null-semilinear-reconstruction-manifest.json"
)
UPSTREAM_DOUBLE_NULL_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-double-null-semilinear-reconstruction/result.json"
)
UPSTREAM_STRICT_NOGO = (
    REPO / "strategy/pre-a-pah1-m2-strict-composition-nogo-manifest.json"
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
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-integrated-{SLUG}/result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT
EXPECTED_PRIMARY_ASSERTIONS = 67
EXPECTED_INDEPENDENT_ASSERTIONS = 37
NEGATIVE_IDS = (
    "NG-2026-08-03-PRE-A-CP1-ST8-CONTINUOUS-TIME-EXACT-CONE",
    "NG-2026-08-03-PRE-A-CP1-ST8-ONE-CONNECTED-SCALAR-EQUIVALENCE",
)


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


def canonical(payload: dict[str, Any]) -> str:
    return json.dumps(
        serial(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


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
        UPSTREAM_LT3,
        UPSTREAM_LT3_RESULT,
        UPSTREAM_PAH1,
        UPSTREAM_PAH1_RESULT,
        UPSTREAM_DOUBLE_NULL,
        UPSTREAM_DOUBLE_NULL_RESULT,
        UPSTREAM_STRICT_NOGO,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required_files:
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "authority",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lt3 = json.loads(UPSTREAM_LT3.read_text(encoding="utf-8"))
    lt3_result = json.loads(UPSTREAM_LT3_RESULT.read_text(encoding="utf-8"))
    pah1 = json.loads(UPSTREAM_PAH1.read_text(encoding="utf-8"))
    pah1_result = json.loads(UPSTREAM_PAH1_RESULT.read_text(encoding="utf-8"))
    double_null = json.loads(UPSTREAM_DOUBLE_NULL.read_text(encoding="utf-8"))
    double_null_result = json.loads(
        UPSTREAM_DOUBLE_NULL_RESULT.read_text(encoding="utf-8")
    )
    strict_nogo = json.loads(UPSTREAM_STRICT_NOGO.read_text(encoding="utf-8"))
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    check(
        "manifest identity and provenance",
        (
            manifest["schema"],
            manifest["candidate_id"],
            manifest["parent_id"],
            manifest["candidate_family"],
            manifest["package_version"],
            manifest["task_id"],
            manifest["claim_context"],
            manifest["comparison_context"],
            manifest["claim_bearing"],
        )
        == (
            MANIFEST_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            CANDIDATE_FAMILY,
            __version__,
            "T-054",
            CLAIM_CONTEXT,
            "A2-FULL-PRODUCTION-WELLPOSED",
            False,
        ),
        (
            manifest["schema"],
            manifest["candidate_id"],
            manifest["parent_id"],
            manifest["candidate_family"],
            manifest["package_version"],
            manifest["task_id"],
            manifest["claim_context"],
            manifest["comparison_context"],
            manifest["claim_bearing"],
        ),
        (
            MANIFEST_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            CANDIDATE_FAMILY,
            __version__,
            "T-054",
            CLAIM_CONTEXT,
            "A2-FULL-PRODUCTION-WELLPOSED",
            False,
        ),
        "identity",
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
    check(
        "manifest artifact key set is exact",
        set(manifest["artifacts"]) == set(expected_artifacts),
        sorted(manifest["artifacts"]),
        sorted(expected_artifacts),
        "artifact_routing",
    )
    for key, path in expected_artifacts.items():
        declared = (REPO / manifest["artifacts"][key]).resolve()
        check(
            f"manifest artifact route: {key}",
            declared == path.resolve(),
            manifest["artifacts"][key],
            str(path.relative_to(REPO)).replace("\\", "/"),
            "artifact_routing",
        )

    manifest_negative_ids = {
        manifest["finite_exact_cone_obstruction"]["negative_id"],
        manifest["restricted_connected_scalar_no_go"]["negative_id"],
    }
    check(
        "manifest negative ids equal the integrated contract",
        manifest_negative_ids == set(NEGATIVE_IDS),
        sorted(manifest_negative_ids),
        sorted(NEGATIVE_IDS),
        "negative_registry",
    )

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    allowed_standard_roots = {
        "__future__",
        "argparse",
        "collections",
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
        "independent route imports only the frozen standard-library set",
        imported_roots == allowed_standard_roots,
        sorted(imported_roots),
        sorted(allowed_standard_roots),
        "independence",
    )

    with tempfile.TemporaryDirectory(prefix="tect-cp1-st8-") as temporary:
        temporary_path = Path(temporary)
        lf_fixture = temporary_path / "lf.txt"
        crlf_fixture = temporary_path / "crlf.txt"
        cr_fixture = temporary_path / "cr.txt"
        lf_fixture.write_bytes(b"alpha\nbeta\n")
        crlf_fixture.write_bytes(b"alpha\r\nbeta\r\n")
        cr_fixture.write_bytes(b"alpha\rbeta\r")
        check(
            "text authority hashes are portable across LF CRLF and lone CR",
            sha256(lf_fixture) == sha256(crlf_fixture) == sha256(cr_fixture),
            (sha256(lf_fixture), sha256(crlf_fixture), sha256(cr_fixture)),
            "one normalized digest",
            "source_integrity",
        )
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

    for label, payload, expected_count, expected_schema, source in (
        ("primary", primary, EXPECTED_PRIMARY_ASSERTIONS, PRIMARY_SCHEMA, PRIMARY),
        (
            "independent",
            independent,
            EXPECTED_INDEPENDENT_ASSERTIONS,
            INDEPENDENT_SCHEMA,
            INDEPENDENT,
        ),
    ):
        check(
            f"{label} identity and parent",
            (
                payload["schema"],
                payload["candidate_id"],
                payload["parent_id"],
                payload["candidate_family"],
                payload["version"],
                payload["task_id"],
                payload["claim_context"],
                payload["comparison_context"],
                payload["claim_bearing"],
            )
            == (
                expected_schema,
                CANDIDATE_ID,
                PARENT_ID,
                CANDIDATE_FAMILY,
                __version__,
                "T-054",
                CLAIM_CONTEXT,
                "A2-FULL-PRODUCTION-WELLPOSED",
                False,
            ),
            (
                payload["schema"],
                payload["candidate_id"],
                payload["parent_id"],
                payload["candidate_family"],
                payload["version"],
                payload["task_id"],
                payload["claim_context"],
                payload["comparison_context"],
                payload["claim_bearing"],
            ),
            (
                expected_schema,
                CANDIDATE_ID,
                PARENT_ID,
                CANDIDATE_FAMILY,
                __version__,
                "T-054",
                CLAIM_CONTEXT,
                "A2-FULL-PRODUCTION-WELLPOSED",
                False,
            ),
            "identity",
        )
        check(
            f"{label} assertion count and all-pass status",
            payload["assertions"]["passed"]
            == payload["assertions"]["total"]
            == expected_count
            and all(row["status"] == "PASS" for row in payload["assertions"]["rows"]),
            (
                payload["assertions"]["passed"],
                payload["assertions"]["total"],
            ),
            (expected_count, expected_count),
            "child_assertions",
        )
        check(
            f"{label} source hash is live",
            payload["source"]["sha256"] == sha256(source),
            payload["source"]["sha256"],
            sha256(source),
            "source_integrity",
        )

    primary_rows = {row["name"]: row for row in primary["assertions"]["rows"]}
    independent_rows = {
        row["name"]: row for row in independent["assertions"]["rows"]
    }
    required_primary_rows = {
        "side 4 staggered sign is periodic on the coarse torus",
        "side 8 staggered sign is periodic on the coarse torus",
        "side 12 staggered sign is periodic on the coarse torus",
        "side 6 hostile control produces an antiperiodic staggered sign",
        "side 4 block transform is an exact signed orthogonal permutation",
        "side 4 axis 0 exact operator Gram conjugacy",
        "side 4 axis 1 exact operator Gram conjugacy",
        "side 4 axis 2 exact operator Gram conjugacy",
        "side 4 fine common stencil kernel has dimension eight",
        "one connected same-dimension standard scalar has nullity one rather than eight",
        "connected standard scalar complete square has two uniform sign minima",
        "the eight folded constant species span the full fine kernel",
        "the LT3-classified 256 fine minima are the eight independent coarse signs",
        "fixed-band harmonic symbol has the Klein-Gordon continuum limit",
        "continuum-symbol leading error is explicitly quadratic in spacing",
        "rescaled harmonic group speed is differentiated from the dispersion",
        "positive mass and the sine identity give the global squared-group-speed bound c over chi",
        "fine LT3 speed and coarse continuum speed agree under the explicit spacing map",
        "PA-H1 circle modes are exactly orthonormal",
        "tuned ordered one-flavour tangent reproduces the PA-H1 quadratic energy",
        "ordered continuum tangent reproduces PA-H1 frequencies three five five",
        "nearest-site response has no constant term and a nonzero t-squared term",
        "distance-two response first appears with the two shortest paths",
        "finite continuous-time displacement response has positive offsite leading coefficients",
    }
    for side in (4, 8, 12):
        required_primary_rows.update(
            {
                f"side {side} fine-to-block coordinate map is bijective",
                f"side {side} staggered transform has an exact inverse",
                f"side {side} staggered transform preserves the symplectic form",
                f"side {side} exact kinetic term block identity",
                f"side {side} exact mass term block identity",
                f"side {side} exact stiffness term block identity",
                f"side {side} exact quartic term block identity",
                f"side {side} full Hamiltonian is the eight-copy block sum",
            }
        )
    check(
        "all load-bearing primary rows are present and pass",
        required_primary_rows.issubset(primary_rows)
        and all(primary_rows[name]["status"] == "PASS" for name in required_primary_rows),
        sorted(required_primary_rows - set(primary_rows)),
        [],
        "load_bearing_rows",
    )

    required_independent_rows = {
        "side 4 direct staggered-periodicity check",
        "side 8 direct staggered-periodicity check",
        "side 12 direct staggered-periodicity check",
        "side 6 direct hostile control is antiperiodic",
        "side 4 folded harmonic spectrum has eight zero modes",
        "direct same-dimension connected standard scalar has one zero mode",
        "direct connected standard complete-square fixture has two uniform signs",
        "direct eight-species signs reproduce the LT3-classified 256 minima",
        "direct fixed-band continuum errors are positive and decrease",
        "direct continuum error divided by spacing squared reaches the derived coefficient",
        "direct positive-mass squared-group-speed samples obey the exact analytic bound",
        "direct fine-to-coarse spacing map preserves the physical squared speed",
        "independent ordered tangent derives PA-H1 squared frequencies",
        "independent circle sampling confirms the PA-H1 mode Gram",
        "direct nearest-site response has a nonzero t-squared coefficient",
        "direct distance-two response has two shortest paths and a nonzero t-fourth coefficient",
    }
    for side in (4, 8, 12):
        required_independent_rows.update(
            {
                f"side {side} direct canonical form equality",
                f"side {side} independent kinetic factorization",
                f"side {side} independent mass factorization",
                f"side {side} independent stiffness factorization",
                f"side {side} independent quartic factorization",
                f"side {side} independent total Hamiltonian factorization",
                f"side {side} direct eight-branch zone-folding identity",
            }
        )
    check(
        "all load-bearing independent rows are present and pass",
        required_independent_rows.issubset(independent_rows)
        and all(
            independent_rows[name]["status"] == "PASS"
            for name in required_independent_rows
        ),
        sorted(required_independent_rows - set(independent_rows)),
        [],
        "load_bearing_rows",
    )

    check(
        "primary independent and manifest scopes agree exactly",
        primary["scope"] == independent["scope"] == manifest["scope"],
        (primary["scope"], independent["scope"], manifest["scope"]),
        "exact equality",
        "scope",
    )
    required_true_scope = {
        "exact_finite_block_canonical_equivalence",
        "eight_decoupled_coarse_species",
        "fine_nodes_are_folded_coarse_zero_modes",
        "finite_quantum_tensor_factorization",
        "periodic_block_factorization_requires_N_divisible_by_four",
        "global_harmonic_group_speed_bound",
        "harmonic_fixed_band_continuum_symbol_limit",
        "tuned_formal_ordered_continuum_pah1_tangent_calibration",
    }
    required_false_scope = {
        "interacting_continuum_limit",
        "quantum_continuum_limit",
        "strict_finite_lattice_causal_cone",
        "finite_lattice_characteristic_sheets",
        "continuum_characteristic_reconstruction",
        "selected_pah1_species_or_sector",
        "full_nonlinear_pah1_embedding",
        "same_selected_state_characteristic_restriction",
        "one_connected_bulk_sector",
        "physical_empty_space",
        "cooling_history",
        "gravity",
        "event_horizon",
        "cp1_complete",
        "pre_a_complete",
    }
    check(
        "scope truth and falsehood contract",
        all(manifest["scope"].get(key) is True for key in required_true_scope)
        and all(manifest["scope"].get(key) is False for key in required_false_scope),
        {
            key: manifest["scope"].get(key)
            for key in sorted(required_true_scope | required_false_scope)
        },
        "required booleans",
        "scope",
    )

    primary_exact = primary["exact_results"]
    independent_exact = independent["exact_results"]
    expected_node_count = int(lt3["exact_classical_theorem"]["node_count"])
    expected_ground_count = int(
        lt3["exact_classical_theorem"]["global_minimum_count"]
    )
    check(
        "kernel ground and connected-comparator counts agree across routes and LT3",
        (
            primary_exact["fine_kernel_dimension"],
            independent_exact["side4_folded_spectrum"]["0"],
            lt3["exact_classical_theorem"]["node_count"],
        )
        == (expected_node_count,) * 3
        and (
            primary_exact["classical_ground_count"],
            independent_exact["ground_count"],
            lt3["exact_classical_theorem"]["global_minimum_count"],
        )
        == (expected_ground_count,) * 3
        and manifest["zone_folding_and_corollaries"]["kernel_dimension"]
        == expected_node_count
        and manifest["zone_folding_and_corollaries"]["classical_ground_count"]
        == expected_ground_count
        and (
            primary_exact["single_connected_standard_scalar_kernel_dimension"],
            independent_exact["same_dimension_connected_zero_modes"],
        )
        == (1, 1)
        and (
            primary_exact["single_connected_standard_scalar_ground_count"],
            independent_exact["same_dimension_connected_ground_count"],
        )
        == (2, 2),
        {
            "kernel": (
                primary_exact["fine_kernel_dimension"],
                independent_exact["side4_folded_spectrum"]["0"],
                lt3["exact_classical_theorem"]["node_count"],
            ),
            "grounds": (
                primary_exact["classical_ground_count"],
                independent_exact["ground_count"],
                lt3["exact_classical_theorem"]["global_minimum_count"],
            ),
        },
        {
            "nodes": expected_node_count,
            "ST8_minima": expected_ground_count,
            "connected_zero_modes": 1,
            "connected_minima": 2,
        },
        "cross_route",
    )
    ground_fixture = primary_exact["classical_ground_fixture_parameters"]
    independent_ground_fixture = independent_exact["ground_fixture_parameters"]
    ground_side = int(ground_fixture["side"])
    ground_r = Fraction(ground_fixture["r"])
    ground_g = Fraction(ground_fixture["g"])
    expected_ground_energy = -Fraction(ground_side**3) * ground_r**2 / (4 * ground_g)
    check(
        "side-four block ground energy agrees with the LT3 complete-square formula",
        ground_fixture == independent_ground_fixture
        and primary_exact["classical_ground_energy_side4_fixture"]
        == str(expected_ground_energy),
        (
            ground_fixture,
            independent_ground_fixture,
            primary_exact["classical_ground_energy_side4_fixture"],
        ),
        (ground_fixture, ground_fixture, str(expected_ground_energy)),
        "cross_route",
    )

    pah1_frequencies = [str(value) for value in pah1["fixture"]["omega"]]
    pah1_frequency_squares = [
        str(Fraction(value) ** 2) for value in pah1_frequencies
    ]
    pah1_mass = Fraction(pah1["fixture"]["mass"])
    expected_calibration = {
        "r": str(-pah1_mass**2 / 2),
        "c": "1",
        "chi": "1",
        "status": "inserted calibration inputs",
    }
    check(
        "PA-H1 calibration parameters circumference and spectrum agree",
        primary_exact["ordered_tangent_calibration_parameters"]
        == independent_exact["ordered_tangent_calibration_parameters"]
        == expected_calibration
        and primary_exact["pah1_circumference"] == "pi/2"
        and independent_exact["pah1_circumference"] == "pi/2"
        and pah1["fixture"]["circumference"] == "pi/2"
        and primary_exact["ordered_potential_curvature"]
        == independent_exact["ordered_potential_curvature"]
        == str(pah1_mass**2)
        and primary_exact["pah1_tangent_frequency_squares"]
        == independent_exact["pah1_tangent_frequency_squares"]
        == pah1_frequency_squares
        and [str(value) for value in primary_exact["pah1_tangent_frequencies"]]
        == [str(value) for value in independent_exact["pah1_tangent_frequencies"]]
        == pah1_frequencies
        and [str(value) for value in manifest["pah1_tangent_calibration"]["frequency_squares"]]
        == pah1_frequency_squares
        and [str(value) for value in manifest["pah1_tangent_calibration"]["frequencies"]]
        == pah1_frequencies,
        {
            "parameters": primary_exact["ordered_tangent_calibration_parameters"],
            "circumference": primary_exact["pah1_circumference"],
            "squares": primary_exact["pah1_tangent_frequency_squares"],
            "frequencies": primary_exact["pah1_tangent_frequencies"],
        },
        {
            "parameters": expected_calibration,
            "circumference": "pi/2",
            "squares": pah1_frequency_squares,
            "frequencies": pah1_frequencies,
        },
        "pah1_calibration",
    )
    check(
        "PA-H1 exact normalized basis agrees with the upstream fixture",
        manifest["pah1_tangent_calibration"]["normalized_basis"]
        == pah1["fixture"]["real_modes"],
        manifest["pah1_tangent_calibration"]["normalized_basis"],
        pah1["fixture"]["real_modes"],
        "pah1_calibration",
    )

    tail_fixture = independent_exact["causal_tail_fixture_parameters"]
    tail_stiffness = Fraction(tail_fixture["c"])
    tail_inertia = Fraction(tail_fixture["chi"])
    expected_d1 = tail_stiffness / (2 * tail_inertia)
    expected_d2 = tail_stiffness**2 / (12 * tail_inertia**2)
    check(
        "symbolic and independent causal-tail coefficients agree after substitution",
        primary_exact["distance_one_response_leading_coefficient"] == "c/(2*chi)"
        and primary_exact["distance_two_response_leading_coefficient"]
        == "c**2/(12*chi**2)"
        and independent_exact["distance_one_response_leading_coefficient"]
        == str(expected_d1)
        and independent_exact["distance_two_response_leading_coefficient"]
        == str(expected_d2),
        (
            primary_exact["distance_one_response_leading_coefficient"],
            primary_exact["distance_two_response_leading_coefficient"],
            independent_exact["distance_one_response_leading_coefficient"],
            independent_exact["distance_two_response_leading_coefficient"],
        ),
        ("c/(2*chi)", "c**2/(12*chi**2)", str(expected_d1), str(expected_d2)),
        "causal_tail",
    )

    speed_fixture = independent_exact["fine_to_coarse_speed_fixture_parameters"]
    speed_spacing = Fraction(speed_fixture["a"])
    speed_physical_stiffness = Fraction(speed_fixture["c_phys"])
    speed_inertia = Fraction(speed_fixture["chi"])
    speed_lattice_stiffness = speed_physical_stiffness / speed_spacing**2
    fine_physical_speed_squared = (
        (speed_spacing / 2) ** 2
        * 4
        * speed_lattice_stiffness
        / speed_inertia
    )
    check(
        "coarse and fine speed conventions are reconciled by the spacing definition",
        primary_exact["coarse_speed_squared"] == "c/chi"
        and lt3["critical_dynamics"]["scalar_speed"] == "c_star=2 sqrt(c/chi)"
        and "coarse-lattice spacing" in primary_exact["coarse_spacing_definition"]
        and "fine-lattice spacing is a/2" in primary_exact["coarse_spacing_definition"]
        and primary_exact["continuum_family_parameter_map"]
        == independent_exact["continuum_family_parameter_map"]
        == "c_LT3(a)=c_phys/a^2 with chi fixed"
        and primary_exact["fine_to_coarse_physical_speed_squared"] == "c/chi"
        and independent_exact["fine_to_coarse_physical_speed_squared_fixture"]
        == str(fine_physical_speed_squared)
        and fine_physical_speed_squared
        == speed_physical_stiffness / speed_inertia,
        (
            primary_exact["coarse_speed_squared"],
            lt3["critical_dynamics"]["scalar_speed"],
            primary_exact["coarse_spacing_definition"],
        ),
        (
            "c/chi",
            "c_star=2 sqrt(c/chi)",
            "coarse a and fine a/2 with c_LT3(a)=c_phys/a^2",
        ),
        "units",
    )

    check(
        "upstream LT3 remains open at continuum characteristic and CP1 gates",
        lt3["scope"]["continuum_limit"] is False
        and lt3["scope"]["characteristic_boundary"] is False
        and lt3["scope"]["cp1_complete"] is False
        and lt3_result["candidate_id"] == PARENT_ID,
        (
            lt3["scope"]["continuum_limit"],
            lt3["scope"]["characteristic_boundary"],
            lt3["scope"]["cp1_complete"],
        ),
        (False, False, False),
        "upstream_scope",
    )
    check(
        "upstream PA-H1 state package still inserts the spectrum and lacks a PA-M2 composition",
        pah1["scope"]["full_pah1_state_selected"] is False
        and pah1["scope"]["kg_operator_or_dispersion_derived"] is False
        and pah1["scope"]["pa_m2_composition"] is False
        and pah1_result["candidate_id"]
        == "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
        (
            pah1["scope"]["full_pah1_state_selected"],
            pah1["scope"]["kg_operator_or_dispersion_derived"],
            pah1["scope"]["pa_m2_composition"],
        ),
        (False, False, False),
        "upstream_scope",
    )
    check(
        "double-null reconstruction still inserts causality and lacks the PA-M2 map",
        double_null["scope"]["causal_structure_inserted"] is True
        and double_null["scope"]["map_to_pa_m2"] is False
        and double_null["scope"]["pre_a_complete"] is False
        and double_null_result["candidate_id"] == "PA-H1-DNKG4-v0",
        (
            double_null["scope"]["causal_structure_inserted"],
            double_null["scope"]["map_to_pa_m2"],
            double_null["scope"]["pre_a_complete"],
        ),
        (True, False, False),
        "upstream_scope",
    )
    check(
        "ST8 lies outside rather than contradicting the strict unchanged-interface no-go",
        strict_nogo["scope"]["ordered_background_flow_embedding_excluded"] is False
        and strict_nogo["scope"]["larger_common_parent_excluded"] is False
        and strict_nogo["scope"]["pre_a_complete"] is False,
        (
            strict_nogo["scope"]["ordered_background_flow_embedding_excluded"],
            strict_nogo["scope"]["larger_common_parent_excluded"],
            strict_nogo["scope"]["pre_a_complete"],
        ),
        (False, False, False),
        "upstream_scope",
    )

    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        slug = negative_id.lower()
        anchor = f'<a id="{slug}"></a>'
        heading = f"### {negative_id} --"
        table_link = f"[{negative_id}](#{slug})"
        check(
            f"negative registry has one anchor heading and table link for {negative_id}",
            registry_text.count(anchor) == 1
            and registry_text.count(heading) == 1
            and registry_text.count(table_link) == 1,
            (
                registry_text.count(anchor),
                registry_text.count(heading),
                registry_text.count(table_link),
            ),
            (1, 1, 1),
            "negative_registry",
        )

    note_text = NOTE.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    required_note_phrases = (
        "eight decoupled ordinary",
        "N=4m+2` produces an antiperiodic",
        "The eight sectors do not interact in v0",
        "the two signs",
        "be the coarse spacing",
        "c_{\\rm LT3}(a)=c_{\\rm phys}/a^2",
        "L=\\pi/2",
        "q_e(t)=\\frac{c}{2\\chi}t^2+O(t^4)",
        "Physical empty space remains unidentified",
        "does not close CP1 or",
    )
    check(
        "certificate contains the load-bearing proof and boundary phrases",
        all(phrase in note_text for phrase in required_note_phrases),
        [phrase for phrase in required_note_phrases if phrase not in note_text],
        [],
        "certificate_scope",
    )
    required_note_anchors = (
        "section-3-exact-full-hamiltonian-factorization",
        "section-7-declared-harmonic-regulator-family",
        "section-8-exact-pa-h1-tangent-calibration",
        "section-9-continuous-time-exact-support-obstruction",
    )
    check(
        "certificate has every exploration evidence anchor exactly once",
        all(
            note_text.count(f'<a id="{anchor}"></a>') == 1
            for anchor in required_note_anchors
        ),
        {
            anchor: note_text.count(f'<a id="{anchor}"></a>')
            for anchor in required_note_anchors
        },
        {anchor: 1 for anchor in required_note_anchors},
        "certificate_scope",
    )
    check(
        "strategy index routes the ST8 package",
        "pre-a-cp1-st8-block-causal-bridge-manifest.json" in index_text
        and "PA-CP1-ST8-CB-v0" in index_text,
        (
            "pre-a-cp1-st8-block-causal-bridge-manifest.json" in index_text,
            "PA-CP1-ST8-CB-v0" in index_text,
        ),
        (True, True),
        "index",
    )
    overclaim_text = " ".join(
        (
            manifest["no_overclaim"],
            primary["no_overclaim"],
            independent["no_overclaim"],
        )
    ).lower()
    for phrase in (
        "interacting or quantum continuum limit",
        "selected pa-h1 species or sector",
        "strict lattice causal cone",
        "connected bulk",
        "physical vacuum",
        "gravity",
        "cp1",
        "pre-a",
    ):
        check(
            f"no-overclaim guard contains {phrase}",
            phrase in overclaim_text,
            phrase in overclaim_text,
            True,
            "overclaim",
        )

    authority_files = (VERIFIER,) + required_files
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "integrated exact finite block, harmonic continuum and causal-boundary audit; not CP1 or Pre-A closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": "A2-FULL-PRODUCTION-WELLPOSED",
        "claim_bearing": False,
        "task_id": "T-054",
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
            "integrated": len(rows),
            "combined": (
                primary["assertions"]["passed"]
                + independent["assertions"]["passed"]
                + len(rows)
            ),
        },
        "scope": manifest["scope"],
        "verdict": manifest["verdict"],
        "negative_ids": list(NEGATIVE_IDS),
        "no_overclaim": manifest["no_overclaim"],
        "assertions": {
            "passed": len(rows),
            "total": len(rows),
            "rows": rows,
        },
        "sources": [
            {
                "path": path.relative_to(REPO),
                "sha256": sha256(path),
            }
            for path in authority_files
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and STORED_INTEGRATED.is_file():
        stored = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError(
                "stored integrated artifact is stale; regenerate without --self-test"
            )
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    counts = payload["child_assertions"]
    print(
        f"PASS {counts['integrated']}/{counts['integrated']} integrated | "
        f"{counts['combined']} combined | {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
