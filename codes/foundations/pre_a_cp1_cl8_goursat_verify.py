#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-CL8-GOURSAT-v0."""

from __future__ import annotations

import argparse
import ast
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
CANDIDATE_ID = "PA-CP1-CL8-GOURSAT-v0"
PARENT_ID = "PA-CP1-ST8-Q3LOCK-v0"
RESULT_ID = "PA-CP1-CL8-CONTINUUM-GOURSAT-ENERGY-SYMPLECTIC-FLUX"
CANDIDATE_FAMILY = "PRE-A-CL8-CONTINUUM-CHARACTERISTIC-RECONSTRUCTION"
SLUG = "pre-a-cp1-cl8-goursat"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_cl8_goursat.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_cl8_goursat_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-goursat-certificate-260803.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
ST8 = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
PAH1 = REPO / "strategy/pre-a-double-null-semilinear-reconstruction-manifest.json"
FINITE_NOGO = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
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

# Explicit assertion-surface oracles.  Changing either child audit requires a
# conscious integrated-verifier review.
EXPECTED_PRIMARY_ASSERTIONS = 53
EXPECTED_INDEPENDENT_ASSERTIONS = 52


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    required = (
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        STRATEGY_INDEX,
        Q3LOCK,
        ST8,
        PAH1,
        FINITE_NOGO,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required:
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "files",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    finite_nogo = json.loads(FINITE_NOGO.read_text(encoding="utf-8"))
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-cl8-goursat-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    identity_tuple = (
        manifest["schema"],
        manifest["candidate_id"],
        manifest["parent_id"],
        manifest["result_id"],
        manifest["candidate_family"],
        manifest["package_version"],
        manifest["task_id"],
        manifest["claim_bearing"],
    )
    expected_identity = (
        MANIFEST_SCHEMA,
        CANDIDATE_ID,
        PARENT_ID,
        RESULT_ID,
        CANDIDATE_FAMILY,
        __version__,
        "T-054",
        False,
    )
    check("manifest identity tuple", identity_tuple == expected_identity, identity_tuple, expected_identity, "identity")
    check("Q3LOCK parent identity", q3lock["candidate_id"] == PARENT_ID, q3lock["candidate_id"], PARENT_ID, "identity")
    check(
        "child identity tuples",
        (
            primary["schema"],
            primary["candidate_id"],
            primary["parent_id"],
            primary["result_id"],
            independent["schema"],
            independent["candidate_id"],
            independent["parent_id"],
            independent["result_id"],
        )
        == (
            PRIMARY_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            RESULT_ID,
            INDEPENDENT_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            RESULT_ID,
        ),
        (
            primary["schema"],
            primary["candidate_id"],
            primary["parent_id"],
            primary["result_id"],
            independent["schema"],
            independent["candidate_id"],
            independent["parent_id"],
            independent["result_id"],
        ),
        (PRIMARY_SCHEMA, CANDIDATE_ID, PARENT_ID, RESULT_ID, INDEPENDENT_SCHEMA, CANDIDATE_ID, PARENT_ID, RESULT_ID),
        "identity",
    )
    check(
        "primary assertion oracle",
        primary["assertions"]["passed"] == primary["assertions"]["total"] == EXPECTED_PRIMARY_ASSERTIONS,
        (primary["assertions"]["passed"], primary["assertions"]["total"]),
        (EXPECTED_PRIMARY_ASSERTIONS, EXPECTED_PRIMARY_ASSERTIONS),
        "children",
    )
    check(
        "independent assertion oracle",
        independent["assertions"]["passed"] == independent["assertions"]["total"] == EXPECTED_INDEPENDENT_ASSERTIONS,
        (independent["assertions"]["passed"], independent["assertions"]["total"]),
        (EXPECTED_INDEPENDENT_ASSERTIONS, EXPECTED_INDEPENDENT_ASSERTIONS),
        "children",
    )

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    check(
        "independent imports neither primary nor symbolic engine",
        not any("pre_a_cp1_cl8_goursat" in name or name.startswith("sympy") for name in imported_modules),
        sorted(imported_modules),
        "no primary or sympy import",
        "independence",
    )

    comparable_keys = (
        "species_count",
        "q3_edge_count",
        "q3_degree",
        "edge_force_bound_coefficient",
        "edge_hessian_row_bound_coefficient",
        "b_R_fixture",
        "ell_R_fixture",
        "self_map_fixture",
        "contraction_fixture",
        "stability_fixture",
        "massless_energy_fixture",
        "negative_unshifted_energy_fixture",
        "symplectic_derivative_first_fixture",
        "symplectic_value_first_hostile_control",
        "physical_3d_weight",
        "reduced_1d_weight_per_unit_transverse_area",
    )
    for key in comparable_keys:
        check(
            f"independent exact agreement: {key}",
            primary["exact_results"][key] == independent["exact_results"][key],
            (primary["exact_results"][key], independent["exact_results"][key]),
            "equal",
            "cross_implementation",
        )

    check(
        "stored primary equals fresh rerun",
        canonical(stored_primary) == canonical(primary),
        sha256(STORED_PRIMARY),
        "fresh canonical JSON",
        "stored_evidence",
    )
    check(
        "stored independent equals fresh rerun",
        canonical(stored_independent) == canonical(independent),
        sha256(STORED_INDEPENDENT),
        "fresh canonical JSON",
        "stored_evidence",
    )

    scope = manifest["scope"]
    for key in (
        "fixed_1_plus_1_lorentzian_background",
        "causal_structure_inserted",
        "transverse_zero_eight_species_classical_field",
        "gated_continuum_goursat_reconstruction",
        "continuum_energy_flux",
        "continuum_variational_symplectic_flux",
        "supplied_classical_measure_pushforward",
    ):
        check(f"manifest positive scope: {key}", scope[key] is True, scope[key], True, "scope")
    for key in (
        "ungated_global_semilinear_existence",
        "full_3_plus_1_dependence",
        "fine_translation_restored",
        "finite_a_goursat_scheme",
        "finite_a_exact_support",
        "lattice_boundary_composition",
        "quantum_or_Hadamard_state_selection",
        "physical_vacuum",
        "below_empty_space",
        "cooling",
        "gravity",
        "event_horizon",
        "CP1_complete",
        "Pre_A_complete",
    ):
        check(f"manifest negative scope: {key}", scope[key] is False, scope[key], False, "scope")
    check(
        "composition gate remains open",
        manifest["composition_gate"]["id"] == "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION"
        and manifest["composition_gate"]["status"].startswith("OPEN"),
        manifest["composition_gate"],
        "open named route gate",
        "scope",
    )
    check(
        "finite strict-cone no-go is retained",
        finite_nogo["scope"]["exact_finite_C1_equilibrium_variational_nogo"] is True
        and finite_nogo["scope"]["controlled_hyperbolic_continuum_limit_rejected"] is False,
        finite_nogo["scope"],
        "finite no-go true and continuum rejection false",
        "scope",
    )

    required_certificate_tokens = (
        "section-5-goursat",
        "section-6-energy",
        "section-7-symplectic",
        "section-8-measure",
        "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION",
        "does not prove ungated",
        "physical-empty-space",
        "CP1",
        "Pre-A",
    )
    for token in required_certificate_tokens:
        check(
            f"certificate token: {token}",
            token in certificate_text,
            token in certificate_text,
            True,
            "certificate",
        )
    check(
        "strategy index route",
        "pre-a-cp1-cl8-goursat-manifest.json" in index_text,
        "pre-a-cp1-cl8-goursat-manifest.json" in index_text,
        True,
        "routing",
    )

    artifacts = manifest["artifacts"]
    expected_artifacts = {
        "certificate": CERTIFICATE,
        "primary_script": PRIMARY,
        "independent_script": INDEPENDENT,
        "integrated_verifier": VERIFIER,
        "primary_result": STORED_PRIMARY,
        "independent_result": STORED_INDEPENDENT,
        "integrated_result": DEFAULT_OUTPUT,
    }
    for key, path in expected_artifacts.items():
        expected_path = str(path.relative_to(REPO)).replace("\\", "/")
        check(f"manifest artifact path: {key}", artifacts[key] == expected_path, artifacts[key], expected_path, "artifacts")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "result_id": RESULT_ID,
        "package_version": __version__,
        "verdict": "PASS",
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "child_assertions": {
            "primary": primary["assertions"]["total"],
            "independent": independent["assertions"]["total"],
        },
        "scope": {
            "claim_bearing": False,
            "gated_continuum_goursat": True,
            "lattice_boundary_composition": False,
            "physical_state_selection": False,
            "physical_empty_space": False,
            "cp1_complete": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "verifier": serial(VERIFIER.relative_to(REPO)),
            "verifier_sha256": sha256(VERIFIER),
            "manifest_sha256": sha256(MANIFEST),
            "certificate_sha256": sha256(CERTIFICATE),
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "stored_primary_sha256": sha256(STORED_PRIMARY),
            "stored_independent_sha256": sha256(STORED_INDEPENDENT),
            "q3lock_sha256": sha256(Q3LOCK),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--selftest", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.selftest and arguments.output == DEFAULT_OUTPUT and DEFAULT_OUTPUT.is_file():
        stored = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError(
                "stored integrated result is stale against the fresh integrated audit"
            )
    if not arguments.selftest:
        atomic_json(arguments.output, payload)
    print(
        f"{CANDIDATE_ID} integrated: {payload['assertions']['passed']}/"
        f"{payload['assertions']['total']} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
