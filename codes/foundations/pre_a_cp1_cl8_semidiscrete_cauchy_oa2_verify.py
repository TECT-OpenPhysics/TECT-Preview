#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0."""

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
CANDIDATE_ID = "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0"
PARENT_ID = "PA-CP1-CL8-GOURSAT-v0"
RESULT_ID = "PA-CP1-CL8-FIXED-DOMAIN-SEMIDISCRETE-CAUCHY-OA2"
CANDIDATE_FAMILY = "PRE-A-CL8-FIXED-DOMAIN-SEMIDISCRETE-CONVERGENCE"
SLUG = "pre-a-cp1-cl8-semidiscrete-cauchy-oa2"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_cl8_semidiscrete_cauchy_oa2.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_cl8_semidiscrete_cauchy_oa2_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-certificate-260803.md"
GOURSAT_MANIFEST = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
FINITE_NOGO = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
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

EXPECTED_PRIMARY_ASSERTIONS = 38
EXPECTED_INDEPENDENT_ASSERTIONS = 29


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
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
        GOURSAT_MANIFEST,
        Q3LOCK,
        FINITE_NOGO,
        STRATEGY_INDEX,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required:
        check(f"required file exists: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    goursat = json.loads(GOURSAT_MANIFEST.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    finite_nogo = json.loads(FINITE_NOGO.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-cl8-sd-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    identity = (
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
    check("manifest identity tuple", identity == expected_identity, identity, expected_identity, "identity")
    check("continuum-definition parent", goursat["candidate_id"] == PARENT_ID, goursat["candidate_id"], PARENT_ID, "identity")
    check("Q3LOCK authority", q3lock["candidate_id"] == "PA-CP1-ST8-Q3LOCK-v0", q3lock["candidate_id"], "PA-CP1-ST8-Q3LOCK-v0", "identity")
    child_identity = (
        primary["schema"],
        primary["candidate_id"],
        primary["parent_id"],
        primary["result_id"],
        independent["schema"],
        independent["candidate_id"],
        independent["parent_id"],
        independent["result_id"],
    )
    expected_child_identity = (
        PRIMARY_SCHEMA,
        CANDIDATE_ID,
        PARENT_ID,
        RESULT_ID,
        INDEPENDENT_SCHEMA,
        CANDIDATE_ID,
        PARENT_ID,
        RESULT_ID,
    )
    check("child identity tuples", child_identity == expected_child_identity, child_identity, expected_child_identity, "identity")
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
        "independent imports neither primary, SymPy, nor flint",
        not any(
            "pre_a_cp1_cl8_semidiscrete" in name
            or name.startswith("sympy")
            or name.startswith("flint")
            for name in imported_modules
        ),
        sorted(imported_modules),
        "no primary, sympy, or flint import",
        "independence",
    )

    comparable_keys = (
        "central_fourth_coefficient",
        "central_sixth_remainder_coefficient",
        "manufactured_residual_coefficient",
        "physical_grid_weight",
        "hamiltonian_fixture_weight",
        "hamiltonian_energy_derivative",
        "variational_symplectic_derivative",
        "ell_R_unit_fixture",
        "gamma_unit_fixture",
        "uniform_residual_constant_fixture",
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
        "independent formal asymptotic coefficient",
        independent["exact_results"]["one_mode_asymptotic_coefficient"]
        == "sin(sqrt(2)/2)/(48*sqrt(2))"
        and independent["exact_results"]["one_mode_rational_multiplier"] == "1/48",
        (
            independent["exact_results"]["one_mode_asymptotic_coefficient"],
            independent["exact_results"]["one_mode_rational_multiplier"],
        ),
        ("sin(sqrt(2)/2)/(48*sqrt(2))", "1/48"),
        "regression",
    )
    arb_result = primary["exact_results"]["arb_regression"]
    check("Arb precision is 160 bits", arb_result["precision_bits"] == 160, arb_result["precision_bits"], 160, "regression")
    check("Arb grid family", arb_result["sizes"] == [16, 32, 64, 128, 256], arb_result["sizes"], [16, 32, 64, 128, 256], "regression")
    check("Arb error count", len(arb_result["errors"]) == 5, len(arb_result["errors"]), 5, "regression")
    check("Arb ratio count", len(arb_result["ratios"]) == 4, len(arb_result["ratios"]), 4, "regression")

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
        "fixed_periodic_domain",
        "fixed_finite_time",
        "smooth_classical_Cauchy_data",
        "weighted_discrete_H1_L2_Oa2",
        "exact_finite_Hamiltonian_conservation",
        "exact_variational_symplectic_conservation",
        "conditional_aggregate_tail_Oa2",
    ):
        check(f"manifest positive scope: {key}", scope[key] is True, scope[key], True, "scope")
    for key in (
        "finite_a_exact_support",
        "pointwise_or_exponential_tail_bound",
        "moving_characteristic_scheme",
        "semidiscrete_Goursat_reconstruction",
        "boundary_to_lattice_composition",
        "continuous_piecewise_linear_H1_Oa2",
        "growing_time_or_volume_uniformity",
        "thermodynamic_limit",
        "full_3_plus_1_dependence",
        "quantum_continuum",
        "selected_state",
        "physical_vacuum",
        "below_empty_space",
        "cooling",
        "gravity",
        "CP1_complete",
        "Pre_A_complete",
    ):
        check(f"manifest negative scope: {key}", scope[key] is False, scope[key], False, "scope")
    check(
        "both packages retain the same open composition gate",
        manifest["composition_gate"]["id"]
        == goursat["composition_gate"]["id"]
        == "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION"
        and manifest["composition_gate"]["status"].startswith("OPEN")
        and goursat["composition_gate"]["status"].startswith("OPEN"),
        (manifest["composition_gate"], goursat["composition_gate"]),
        "same open route gate",
        "scope",
    )
    check(
        "finite-a no-go remains authoritative",
        finite_nogo["scope"]["exact_finite_C1_equilibrium_variational_nogo"] is True
        and primary["scope"]["finite_a_exact_support"] is False,
        (
            finite_nogo["scope"]["exact_finite_C1_equilibrium_variational_nogo"],
            primary["scope"]["finite_a_exact_support"],
        ),
        (True, False),
        "scope",
    )
    check(
        "Arb regression explicitly is not proof",
        manifest["arb_regression"]["regression_is_proof"] is False
        and primary["scope"]["arb_regression_is_theorem"] is False,
        (
            manifest["arb_regression"]["regression_is_proof"],
            primary["scope"]["arb_regression_is_theorem"],
        ),
        (False, False),
        "scope",
    )

    required_certificate_tokens = (
        "section-4-hamiltonian",
        "section-5-consistency",
        "section-6-theorem",
        "section-7-tail",
        "section-8-arb",
        "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION",
        "not a semidiscrete Goursat theorem",
        "piecewise-linear",
        "physical empty space",
        "CP1",
        "Pre-A",
    )
    for token in required_certificate_tokens:
        check(f"certificate token: {token}", token in certificate_text, token in certificate_text, True, "certificate")
    check(
        "strategy index route",
        "pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json" in index_text,
        "pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json" in index_text,
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
            "fixed_domain_smooth_Cauchy_Oa2": True,
            "finite_a_exact_support": False,
            "semidiscrete_Goursat": False,
            "boundary_to_lattice_composition": False,
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
            "goursat_manifest_sha256": sha256(GOURSAT_MANIFEST),
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
