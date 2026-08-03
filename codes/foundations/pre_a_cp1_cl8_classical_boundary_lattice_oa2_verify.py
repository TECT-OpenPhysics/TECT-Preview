#!/usr/bin/env python3
"""Integrated verifier for the classical CL8 boundary-to-lattice bridge."""

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
CANDIDATE_ID = "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-GOURSAT-PHASE-SLICE-SEMIDISCRETE-COMPOSITION-OA2"
CANDIDATE_FAMILY = "PRE-A-CL8-CLASSICAL-CHARACTERISTIC-TO-REGULATOR-COMPOSITION"
SLUG = "pre-a-cp1-cl8-classical-boundary-lattice-oa2"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_cl8_classical_boundary_lattice_oa2.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_cl8_classical_boundary_lattice_oa2_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-certificate-260803.md"
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
BLOCK = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
FINITE_NOGO = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
GOURSAT_CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-goursat-certificate-260803.md"
SEMIDISCRETE_CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-certificate-260803.md"
GOURSAT_INTEGRATED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-cl8-goursat/result.json"
SEMIDISCRETE_INTEGRATED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-cl8-semidiscrete-cauchy-oa2/result.json"
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
EXPECTED_PRIMARY_ASSERTIONS = 49
EXPECTED_INDEPENDENT_ASSERTIONS = 38


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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
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
        GOURSAT,
        SEMIDISCRETE,
        BLOCK,
        Q3LOCK,
        FINITE_NOGO,
        GOURSAT_CERTIFICATE,
        SEMIDISCRETE_CERTIFICATE,
        GOURSAT_INTEGRATED,
        SEMIDISCRETE_INTEGRATED,
        STRATEGY_INDEX,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required:
        check(f"required file exists: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    finite_nogo = json.loads(FINITE_NOGO.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-cl8-compose-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    identity = (
        manifest["schema"],
        manifest["candidate_id"],
        tuple(manifest["parent_ids"]),
        manifest["result_id"],
        manifest["candidate_family"],
        manifest["package_version"],
        manifest["task_id"],
        manifest["claim_bearing"],
    )
    expected_identity = (
        MANIFEST_SCHEMA,
        CANDIDATE_ID,
        PARENT_IDS,
        RESULT_ID,
        CANDIDATE_FAMILY,
        __version__,
        "T-054",
        False,
    )
    check("manifest identity tuple", identity == expected_identity, identity, expected_identity, "identity")
    check("Goursat parent identity", goursat["candidate_id"] == PARENT_IDS[0], goursat["candidate_id"], PARENT_IDS[0], "identity")
    check("semidiscrete parent identity", semidiscrete["candidate_id"] == PARENT_IDS[1], semidiscrete["candidate_id"], PARENT_IDS[1], "identity")
    check("Q3LOCK authority identity", q3lock["candidate_id"] == "PA-CP1-ST8-Q3LOCK-v0", q3lock["candidate_id"], "PA-CP1-ST8-Q3LOCK-v0", "identity")
    check(
        "parent packages remain claim-nonbearing",
        goursat["claim_bearing"] is False and semidiscrete["claim_bearing"] is False,
        (goursat["claim_bearing"], semidiscrete["claim_bearing"]),
        (False, False),
        "identity",
    )
    check(
        "physical one-eighth normalization crosses both parents",
        "1/8" in goursat["definition"]["physical_normalization"]
        and "a/8" in semidiscrete["definition"]["weighted_inner_product"],
        (
            goursat["definition"]["physical_normalization"],
            semidiscrete["definition"]["weighted_inner_product"],
        ),
        "continuum 1/8 and grid a/8",
        "identity",
    )
    check(
        "manifest Q3LOCK authority path",
        manifest["authorities"]["nonlinear_Q3_model"] == str(Q3LOCK.relative_to(REPO)).replace("\\", "/"),
        manifest["authorities"]["nonlinear_Q3_model"],
        str(Q3LOCK.relative_to(REPO)).replace("\\", "/"),
        "identity",
    )
    child_identity = (
        primary["schema"],
        primary["candidate_id"],
        tuple(primary["parent_ids"]),
        primary["result_id"],
        independent["schema"],
        independent["candidate_id"],
        tuple(independent["parent_ids"]),
        independent["result_id"],
    )
    expected_child_identity = (
        PRIMARY_SCHEMA,
        CANDIDATE_ID,
        PARENT_IDS,
        RESULT_ID,
        INDEPENDENT_SCHEMA,
        CANDIDATE_ID,
        PARENT_IDS,
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
            "pre_a_cp1_cl8_classical_boundary" in name
            or name.startswith("sympy")
            or name.startswith("flint")
            for name in imported_modules
        ),
        sorted(imported_modules),
        "no primary, sympy, or flint import",
        "independence",
    )

    comparable_keys = (
        "q_hermite_determinant",
        "q_hermite_coefficients",
        "pi_hermite_determinant",
        "pi_hermite_coefficients",
        "real_nyquist_squared_norm_ratio",
        "spectral_multiplier_endpoint",
        "sampling_kernel_symplectic_fixture",
        "measure_coupling_cost_fixture",
    )
    for key in comparable_keys:
        check(
            f"independent exact agreement: {key}",
            primary["exact_results"][key] == independent["exact_results"][key],
            (primary["exact_results"][key], independent["exact_results"][key]),
            "equal",
            "cross_implementation",
        )
    for key in ("pah1_ordered_q_lower", "pah1_shifted_q_lower"):
        normalized_pair = tuple(value.replace("^", "**") for value in (primary["exact_results"][key], independent["exact_results"][key]))
        check(
            f"independent exact agreement after exponent notation normalization: {key}",
            normalized_pair[0] == normalized_pair[1],
            normalized_pair,
            "equal",
            "cross_implementation",
        )
    check(
        "primary and independent energy-series coefficients agree",
        primary["exact_results"]["gradient_symbol_series"] == "(a**4 - 30*a**2 + 360)/360"
        and independent["exact_results"]["gradient_symbol_coefficients"] == ["1", "-1/12", "1/360"]
        and independent["exact_results"]["physical_gradient_coefficients"] == ["-1/192", "1/5760"],
        (
            primary["exact_results"]["gradient_symbol_series"],
            independent["exact_results"]["gradient_symbol_coefficients"],
            independent["exact_results"]["physical_gradient_coefficients"],
        ),
        ("1-a^2/12+a^4/360", ["1", "-1/12", "1/360"], ["-1/192", "1/5760"]),
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

    common_gate = "PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION"
    check(
        "parent common gate preserved",
        goursat["composition_gate"]["id"] == semidiscrete["composition_gate"]["id"] == common_gate,
        (goursat["composition_gate"]["id"], semidiscrete["composition_gate"]["id"]),
        common_gate,
        "gate_split",
    )
    resolution = manifest["composition_gate_resolution"]
    check("original gate resolved by split", resolution["original_id"] == common_gate and resolution["status"] == "RESOLVED BY SCOPE SPLIT", (resolution["original_id"], resolution["status"]), (common_gate, "RESOLVED BY SCOPE SPLIT"), "gate_split")
    check(
        "classical kinematic and preferred-state subgates separated",
        resolution["closed_classical_subgate"] == "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-COMPOSITION"
        and resolution["open_state_selection_subgate"] == "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION",
        (resolution["closed_classical_subgate"], resolution["open_state_selection_subgate"]),
        ("classical kinematic composition closed", "preferred-state selection open"),
        "gate_split",
    )
    mapping_text = canonical(resolution["mapping"])
    mapping_upper = mapping_text.upper()
    for token in ("PROVED", "MOVED", "NOT REQUIRED", "finite-a", "preferred or invariant classical-measure selection", "quantum-state composition"):
        check(f"gate mapping token: {token}", token.upper() in mapping_upper, token.upper() in mapping_upper, True, "gate_split")
    check(
        "next route gates remain open",
        all(entry["status"].startswith("OPEN") for entry in manifest["next_route_gates"].values()),
        manifest["next_route_gates"],
        "all open",
        "gate_split",
    )
    expected_parent_missing = {
        (goursat["candidate_id"], text)
        for text in goursat["composition_gate"]["missing"]
    } | {
        (semidiscrete["candidate_id"], text)
        for text in semidiscrete["composition_gate"]["missing"]
    }
    coverage_rows = manifest["parent_missing_coverage"]
    actual_parent_missing = {
        (row["parent_id"], row["parent_text"])
        for row in coverage_rows
    }
    check(
        "parent missing obligations covered exactly once",
        len(coverage_rows) == len(actual_parent_missing) == len(expected_parent_missing)
        and actual_parent_missing == expected_parent_missing,
        {
            "rows": len(coverage_rows),
            "unique": len(actual_parent_missing),
            "actual": sorted(actual_parent_missing),
        },
        {"count": len(expected_parent_missing), "expected": sorted(expected_parent_missing)},
        "gate_split",
    )
    for row in coverage_rows:
        check(
            f"coverage disposition and anchor: {row['parent_id']} :: {row['parent_text']}",
            bool(row["disposition"])
            and row["certificate_anchor"] in certificate_text
            and row["disposition"]
            == row["disposition"].upper(),
            (row["disposition"], row["certificate_anchor"]),
            "uppercase disposition and existing certificate anchor",
            "gate_split",
        )

    positive_scope = (
        "fixed_1_plus_1_lorentzian_background",
        "classical_phase_slice",
        "direct_periodic_seam_composition",
        "generic_declared_hermite_extension_composition",
        "fixed_domain_time_regulator_Oa2",
        "trigonometric_H1_L2_Oa2",
        "energy_sampling_Oa2",
        "variational_symplectic_sampling_Oa2",
        "supplied_classical_phase_measure_W1_Oa2",
    )
    negative_scope = (
        "generic_direct_periodic_composition_without_extra_data",
        "canonical_extension",
        "finite_a_exact_energy_or_symplectic_sampling",
        "finite_a_exact_support",
        "semidiscrete_Goursat_scheme",
        "moving_characteristic_boundary",
        "full_pah1_circumference_current_gate",
        "growing_time_or_volume_uniformity",
        "thermodynamic_limit",
        "full_3_plus_1_dependence",
        "quantum_continuum",
        "selected_classical_measure",
        "selected_state",
        "physical_vacuum",
        "below_empty_space",
        "cooling",
        "gravity",
        "event_horizon",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in positive_scope:
        check(f"manifest positive scope: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in negative_scope:
        check(f"manifest negative scope: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    check(
        "finite-a strict-cone no-go retained",
        finite_nogo["scope"]["exact_finite_C1_equilibrium_variational_nogo"] is True
        and manifest["scope"]["finite_a_exact_support"] is False,
        (
            finite_nogo["scope"]["exact_finite_C1_equilibrium_variational_nogo"],
            manifest["scope"]["finite_a_exact_support"],
        ),
        (True, False),
        "scope",
    )
    check(
        "PA-H1 calibration source retained",
        block["pah1_tangent_calibration"]["ordered_curvature"] == "-2r/chi=9",
        block["pah1_tangent_calibration"]["ordered_curvature"],
        "-2r/chi=9",
        "calibration",
    )

    required_certificate_tokens = (
        "section-3-generic-obstruction",
        "section-5-domain-branches",
        "section-6-cauchy",
        "section-8-energy",
        "section-9-symplectic",
        "section-10-reconstruction",
        "section-11-measure",
        "section-13-calibration",
        "section-14-gate-split",
        "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION",
        "9\\pi^2\\over32",
        "H_{\\rm ext}",
        "W_1^X",
        "not a finite-`a` Goursat scheme",
        "physical empty space",
        "CP1",
        "Pre-A",
    )
    for token in required_certificate_tokens:
        check(f"certificate token: {token}", token in certificate_text, token in certificate_text, True, "certificate")
    check(
        "strategy index route",
        "pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json" in index_text,
        "pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json" in index_text,
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
        "parent_ids": list(PARENT_IDS),
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
            "classical_composition_subgate_closed": True,
            "preferred_state_composition_open": True,
            "full_circumference_goursat_open": True,
            "finite_a_exact_sampling": False,
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
            "goursat_manifest_sha256": sha256(GOURSAT),
            "semidiscrete_manifest_sha256": sha256(SEMIDISCRETE),
            "block_manifest_sha256": sha256(BLOCK),
            "q3lock_manifest_sha256": sha256(Q3LOCK),
            "finite_nogo_manifest_sha256": sha256(FINITE_NOGO),
            "goursat_certificate_sha256": sha256(GOURSAT_CERTIFICATE),
            "semidiscrete_certificate_sha256": sha256(SEMIDISCRETE_CERTIFICATE),
            "goursat_integrated_sha256": sha256(GOURSAT_INTEGRATED),
            "semidiscrete_integrated_sha256": sha256(SEMIDISCRETE_INTEGRATED),
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
            raise AssertionError("stored integrated result is stale against the fresh integrated audit")
    if not arguments.selftest:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID} integrated: {payload['assertions']['passed']}/{payload['assertions']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
