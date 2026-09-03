#!/usr/bin/env python3
"""Integrated hostile verifier for global CL8 Goursat continuation.

Changelog: 0.1.1 (2026-08-04) adds clipped-Bielecki and canonical-PDF QA.
"""

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

import pdfplumber
from PIL import Image, ImageStat
from pypdf import PdfReader


__version__ = "0.1.1"
__first_issued__ = "2026-08-03"
__version_issued__ = "2026-08-04"
__claims__ = ["C6-SPACETIME-SIGNATURE"]
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-FINITE-TRIANGLE-GOURSAT-GLOBAL-EXISTENCE-STABILITY"
CANDIDATE_FAMILY = "PRE-A-CL8-GLOBAL-CHARACTERISTIC-CONTINUATION"
SLUG = "pre-a-cp1-cl8-global-goursat-continuation"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_cl8_global_goursat_continuation.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_independent.py"
PDF_BUILDER = REPO / "codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_pdf.py"
PDF = REPO / "output/pdf/pre-a-cp1-cl8-global-goursat-continuation-certificate-260803-260804-v0.1.1.pdf"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260803.md"
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
GOURSAT_CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-goursat-certificate-260803.md"
GOURSAT_INTEGRATED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-cl8-goursat/result.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
COMPOSITION_CERTIFICATE = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-certificate-260803.md"
COMPOSITION_INTEGRATED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-cl8-classical-boundary-lattice-oa2/result.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
BLOCK = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
FINITE_NOGO = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-integrated-{SLUG}/result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT
EXPECTED_PRIMARY_ASSERTIONS = 68
EXPECTED_INDEPENDENT_ASSERTIONS = 65
EXPECTED_INTEGRATED_ASSERTIONS = 159
EXPECTED_AUTHORITY_HASHES = {
    "composition_manifest": "6f046b62c99c43ac6c04de546669f635cfb079c3c5ecad5e09bb7e6674a8d0b6",
    "composition_certificate": "3d3464c0e32c6020185a9fd9b72449932f53aaeb842241353d89342f93047f2b",
    "composition_integrated": "58e7e71862220a9c20fb10e8851efcc65b70f9a23ebb98eabf6b134b0632d6ed",
    "goursat_manifest": "571ac5cd92fffd25e14da57ec9c4ef17e2550f72718d739f1a335dfb27c4647b",
    "goursat_certificate": "5472a71f29ba49b1cbaae05c8cf2eab99d6fad64f2e14a5008ee624c29d457fc",
    "goursat_integrated": "1ff142b9d03cca31a994da945e7940b4e4110e5a93d49891ab5b410760289574",
    "q3lock_manifest": "d49686f88833f323beabd2953eb50d0a1083d3d71fcc28e27da6a4d2b3b81046",
    "block_manifest": "b0a8ddec5c5082da816d352f09affc8e5226a31106842b106920f49402879bcb",
    "finite_nogo_manifest": "9e2f30847c8f6d2a4b0ca33de65eeaff763374c2d729bdf47a5bfc4cd577398a",
    "c6_status": "a0d6d7cd99770cd97050eb28fc4dc69180191ba930de629ee023cffc3a2aa811",
}


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted(serial(item) for item in value)
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



def find_pdftoppm() -> Path:
    candidates = [
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(
        Path.home().glob(
            ".cache/codex-runtimes/*/dependencies/native/poppler/Library/bin/pdftoppm.exe"
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise AssertionError("pdftoppm unavailable")


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
        PDF_BUILDER,
        PDF,
        MANIFEST,
        CERTIFICATE,
        GOURSAT,
        GOURSAT_CERTIFICATE,
        GOURSAT_INTEGRATED,
        COMPOSITION,
        COMPOSITION_CERTIFICATE,
        COMPOSITION_INTEGRATED,
        Q3LOCK,
        BLOCK,
        FINITE_NOGO,
        C6_STATUS,
        NEGATIVE_REGISTRY,
        STRATEGY_INDEX,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required:
        check(f"required file exists: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))
    c6 = json.loads(C6_STATUS.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-cl8-global-goursat-") as directory:
        temporary = Path(directory)
        fresh_primary = run_child(PRIMARY, temporary / "primary.json")
        fresh_independent = run_child(INDEPENDENT, temporary / "independent.json")

    check("manifest schema", manifest["schema"] == MANIFEST_SCHEMA, manifest["schema"], MANIFEST_SCHEMA, "identity")
    check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    check("parent identities", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    check("candidate family", manifest["candidate_family"] == CANDIDATE_FAMILY, manifest["candidate_family"], CANDIDATE_FAMILY, "identity")
    check("primary schema", fresh_primary["schema"] == PRIMARY_SCHEMA, fresh_primary["schema"], PRIMARY_SCHEMA, "identity")
    check("independent schema", fresh_independent["schema"] == INDEPENDENT_SCHEMA, fresh_independent["schema"], INDEPENDENT_SCHEMA, "identity")
    check("child candidate agreement", fresh_primary["candidate_id"] == fresh_independent["candidate_id"] == CANDIDATE_ID, [fresh_primary["candidate_id"], fresh_independent["candidate_id"]], [CANDIDATE_ID, CANDIDATE_ID], "identity")
    check("child result agreement", fresh_primary["result_id"] == fresh_independent["result_id"] == RESULT_ID, [fresh_primary["result_id"], fresh_independent["result_id"]], [RESULT_ID, RESULT_ID], "identity")
    check("claim nonbearing manifest", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    check("claim nonbearing primary", fresh_primary["claim_bearing"] is False, fresh_primary["claim_bearing"], False, "identity")
    check("claim nonbearing independent", fresh_independent["claim_bearing"] is False, fresh_independent["claim_bearing"], False, "identity")

    check("primary exact assertion count", fresh_primary["assertion_summary"] == {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, fresh_primary["assertion_summary"], {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, "children")
    check("independent exact assertion count", fresh_independent["assertion_summary"] == {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, fresh_independent["assertion_summary"], {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, "children")
    check("primary all PASS", all(row["status"] == "PASS" for row in fresh_primary["assertions"]), {row["status"] for row in fresh_primary["assertions"]}, {"PASS"}, "children")
    check("independent all PASS", all(row["status"] == "PASS" for row in fresh_independent["assertions"]), {row["status"] for row in fresh_independent["assertions"]}, {"PASS"}, "children")
    check("stored primary equals fresh", canonical(stored_primary) == canonical(fresh_primary), sha256(STORED_PRIMARY), "fresh canonical payload", "freshness")
    check("stored independent equals fresh", canonical(stored_independent) == canonical(fresh_independent), sha256(STORED_INDEPENDENT), "fresh canonical payload", "freshness")

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"), filename=str(INDEPENDENT))
    imports: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    check("independent does not import primary", "pre_a_cp1_cl8_global_goursat_continuation" not in imports, sorted(imports), "no primary import", "independence")
    check("independent does not import SymPy", "sympy" not in imports, sorted(imports), "no sympy", "independence")
    check("independent does not import flint", "flint" not in imports, sorted(imports), "no flint", "independence")

    p_derived = fresh_primary["derived"]
    i_derived = fresh_independent["derived"]
    check("Q3 derivations agree", p_derived["q3"] == i_derived["q3"], p_derived["q3"], i_derived["q3"], "cross")
    for key in (
        "C_star",
        "boundary_flux",
        "slice_energy",
        "S_tau",
        "b_S",
        "ell_S",
        "K0",
        "R_c",
        "b_Rc",
        "ell_Rc",
        "delta_squared",
        "shell_selfmap",
        "shell_contraction",
    ):
        check(f"test fixture agrees: {key}", p_derived["test_fixture"][key] == i_derived["test_fixture"][key], p_derived["test_fixture"][key], i_derived["test_fixture"][key], "cross")
    check("Bessel coefficients agree", p_derived["bessel_coefficients"] == i_derived["bessel_coefficients"], p_derived["bessel_coefficients"], i_derived["bessel_coefficients"], "cross")
    expected_bielecki = {"R_bar": "5", "b_Rbar": "130", "ell_Rbar": "76", "beta_squared": "38", "contraction": "1/2", "first_exit_margin": "1"}
    check("clipped-Bielecki fixtures agree", p_derived["bielecki_alternative"] == i_derived["bielecki_alternative"] == expected_bielecki, [p_derived["bielecki_alternative"], i_derived["bielecki_alternative"]], [expected_bielecki, expected_bielecki], "cross")
    check("high-regularity structures agree", p_derived["high_regularity"] == i_derived["high_regularity"], p_derived["high_regularity"], i_derived["high_regularity"], "cross")
    check("PA-H1 frequency squares agree", p_derived["pah1"]["frequency_squares"] == i_derived["pah1"]["frequency_squares"], p_derived["pah1"]["frequency_squares"], i_derived["pah1"]["frequency_squares"], "cross")
    check("linearized-control flags agree", p_derived["pah1"]["linearized_control_only"] is True and i_derived["pah1"]["linearized_control_only"] is True, [p_derived["pah1"]["linearized_control_only"], i_derived["pah1"]["linearized_control_only"]], [True, True], "cross")
    check("linearized ell=9chi shell count agrees", p_derived["pah1"]["linearized_shifted_shells"] == i_derived["pah1"]["linearized_shifted_shells"], p_derived["pah1"]["linearized_shifted_shells"], i_derived["pah1"]["linearized_shifted_shells"], "cross")
    check("linearized ell=18chi shell count agrees", p_derived["pah1"]["linearized_unshifted_shells"] == i_derived["pah1"]["linearized_unshifted_shells"], p_derived["pah1"]["linearized_unshifted_shells"], i_derived["pah1"]["linearized_unshifted_shells"], "cross")
    check("primary old unshifted formula", p_derived["pah1"]["old_unshifted_q"] == "9*pi**2/32", p_derived["pah1"]["old_unshifted_q"], "9*pi**2/32", "cross")
    check("primary old shifted formula", p_derived["pah1"]["old_shifted_q"] == "9*pi**2/64", p_derived["pah1"]["old_shifted_q"], "9*pi**2/64", "cross")
    check("independent old unshifted coefficient", i_derived["pah1"]["old_unshifted_q_pi2_coefficient"] == "9/32", i_derived["pah1"]["old_unshifted_q_pi2_coefficient"], "9/32", "cross")
    check("independent old shifted coefficient", i_derived["pah1"]["old_shifted_q_pi2_coefficient"] == "9/64", i_derived["pah1"]["old_shifted_q_pi2_coefficient"], "9/64", "cross")
    check("primary linearized ell=9chi shell formula", p_derived["pah1"]["linearized_shifted_shell_q"] == "9*pi**2/128", p_derived["pah1"]["linearized_shifted_shell_q"], "9*pi**2/128", "cross")
    check("primary linearized ell=18chi shell formula", p_derived["pah1"]["linearized_unshifted_shell_q"] == "pi**2/16", p_derived["pah1"]["linearized_unshifted_shell_q"], "pi**2/16", "cross")
    check("independent linearized ell=9chi shell coefficient", i_derived["pah1"]["linearized_shifted_shell_q_pi2_coefficient"] == "9/128", i_derived["pah1"]["linearized_shifted_shell_q_pi2_coefficient"], "9/128", "cross")
    check("independent linearized ell=18chi shell coefficient", i_derived["pah1"]["linearized_unshifted_shell_q_pi2_coefficient"] == "1/16", i_derived["pah1"]["linearized_unshifted_shell_q_pi2_coefficient"], "1/16", "cross")
    check("periodic phase turns", i_derived["periodic_fixture"]["phase_turns"] == "2", i_derived["periodic_fixture"]["phase_turns"], "2", "cross")

    authority_paths = {
        "composition_manifest": COMPOSITION,
        "composition_certificate": COMPOSITION_CERTIFICATE,
        "composition_integrated": COMPOSITION_INTEGRATED,
        "goursat_manifest": GOURSAT,
        "goursat_certificate": GOURSAT_CERTIFICATE,
        "goursat_integrated": GOURSAT_INTEGRATED,
        "q3lock_manifest": Q3LOCK,
        "block_manifest": BLOCK,
        "finite_nogo_manifest": FINITE_NOGO,
        "c6_status": C6_STATUS,
    }
    authority_hashes = {name: sha256(path) for name, path in authority_paths.items()}
    for name, expected in EXPECTED_AUTHORITY_HASHES.items():
        check(f"authority hash pinned: {name}", authority_hashes[name] == expected, authority_hashes[name], expected, "provenance")
    for child_name, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        check(f"{child_name} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "provenance")
        check(f"{child_name} Goursat hash", child["source_sha256"]["goursat_manifest"] == sha256(GOURSAT), child["source_sha256"]["goursat_manifest"], sha256(GOURSAT), "provenance")
        check(f"{child_name} composition hash", child["source_sha256"]["composition_manifest"] == sha256(COMPOSITION), child["source_sha256"]["composition_manifest"], sha256(COMPOSITION), "provenance")
        check(f"{child_name} Q3LOCK hash", child["source_sha256"]["q3lock_manifest"] == sha256(Q3LOCK), child["source_sha256"]["q3lock_manifest"], sha256(Q3LOCK), "provenance")
        check(f"{child_name} calibration hash", child["source_sha256"]["block_manifest"] == sha256(BLOCK), child["source_sha256"]["block_manifest"], sha256(BLOCK), "provenance")

    gate = manifest["gate_resolution"]
    check("gate id exact", gate["id"] == "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", gate["id"], "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", "gate")
    check("parent gate stays historical OPEN", composition["next_route_gates"]["full_circumference"]["status"] == "OPEN MANIFEST-LOCAL ROUTE GATE", composition["next_route_gates"]["full_circumference"]["status"], "OPEN MANIFEST-LOCAL ROUTE GATE", "gate")
    check("successor scoped closure", gate["status"] == "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", gate["status"], "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", "gate")
    check("preferred-state next gate", gate["next_gate"] == "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION", gate["next_gate"], "PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION", "gate")
    check("parent Goursat ungated flag remains false", goursat["scope"]["ungated_global_semilinear_existence"] is False, goursat["scope"]["ungated_global_semilinear_existence"], False, "gate")
    check("finite-regulator no-go is a manifest authority", manifest["authorities"]["finite_regulator_strict_cone_boundary"] == "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json", manifest["authorities"]["finite_regulator_strict_cone_boundary"], "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json", "gate")
    check("unmatched periodic no-go is preserved in manifest", "NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION" in manifest["hostile_boundaries"]["registered_same_domain_no_go"], manifest["hostile_boundaries"]["registered_same_domain_no_go"], "contains registered no-go", "gate")

    scope = manifest["scope"]
    true_flags = (
        "arbitrary_finite_triangle_goursat_existence",
        "global_classical_uniqueness",
        "explicit_amplitude_bound",
        "global_field_value_stability",
        "full_pah1_circumference_classical_gate",
        "nonconstant_periodic_ordered_trace_family",
    )
    false_flags = (
        "periodic_seams_automatic",
        "causal_structure_derived",
        "full_3_plus_1_dependence",
        "gravity_constraints",
        "finite_a_goursat_scheme",
        "growing_time_uniformity",
        "thermodynamic_limit",
        "selected_classical_measure",
        "selected_state",
        "quantum_or_Hadamard_state",
        "physical_vacuum",
        "below_empty_space",
        "cooling",
        "gravity",
        "event_horizon",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for flag in true_flags:
        check(f"scope true: {flag}", scope[flag] is True, scope[flag], True, "scope")
    for flag in false_flags:
        check(f"scope false: {flag}", scope[flag] is False, scope[flag], False, "scope")
    check("child scopes agree", fresh_primary["scope"] == fresh_independent["scope"] == scope, [fresh_primary["scope"], fresh_independent["scope"]], [scope, scope], "scope")

    check("C6 tier unchanged", c6["tier"] == "T1", c6["tier"], "T1", "claim-boundary")
    check("C6 lifecycle unchanged", c6["lifecycle"] == "ACTIVE", c6["lifecycle"], "ACTIVE", "claim-boundary")
    check("C6 remains conditional", c6["evidence_grade"] == ["CONDITIONAL"], c6["evidence_grade"], ["CONDITIONAL"], "claim-boundary")
    check("C6 premise gate unchanged", c6["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim-boundary")
    for negative_id in (
        "NG-2026-08-03-PRE-A-CP1-FINITE-C1-EQUILIBRIUM-STRICT-CONE",
        "NG-2026-08-03-PRE-A-CP1-ST8-CONTINUOUS-TIME-EXACT-CONE",
        "NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION",
    ):
        check(f"strict-cone negative retained: {negative_id}", negative_id in negative_text, negative_id in negative_text, True, "claim-boundary")

    anchors = (
        'id="section-4-shift"',
        'id="section-5-flux"',
        'id="section-6-amplitude"',
        'id="section-7-continuation"',
        'id="section-7-1-bielecki"',
        'id="section-8-stability"',
        'id="section-9-pah1"',
        'id="section-10-gate"',
        'id="section-11-adversarial"',
        'id="section-13-no-overclaim"',
    )
    for anchor in anchors:
        check(f"certificate anchor: {anchor}", anchor in certificate_text, anchor in certificate_text, True, "certificate")
    check("high-regularity lemma present", "### 8.1 High-regularity phase-map lemma" in certificate_text and "D_m" in certificate_text and "D_{m-1}" in certificate_text and "P_{m-1}" in certificate_text, ["### 8.1 High-regularity phase-map lemma" in certificate_text, "D_m" in certificate_text, "D_{m-1}" in certificate_text, "P_{m-1}" in certificate_text], [True, True, True, True], "certificate")
    alternate = manifest["alternate_bielecki_proof"]
    alternate_surface = [
        "### 7.1 Alternate whole-triangle clipped-Bielecki audit" in certificate_text,
        "EXP-000734" in certificate_text,
        "introduces no new theorem" in certificate_text,
        "first contact" in certificate_text,
        alternate["route_record"] == "EXP-000737",
        "NO NEW THEOREM, RESULT, GATE, OR SCOPE" in alternate["status"],
        "D_(m-1)" in alternate["high_regularity_boundary"],
        "EXP-000735" in alternate["high_regularity_boundary"],
    ]
    check("clipped-Bielecki audit is alternate and high-regularity authority preserved", all(alternate_surface), alternate_surface, [True] * len(alternate_surface), "certificate")
    required_phrases = (
        "unknown cap of area",
        "Bessel-`I0` stability estimate",
        "nonconstant seam-compatible periodic trace",
        "does not make arbitrary Goursat traces periodic",
        "physical empty space",
        "CP1 and Pre-A remain open",
        "NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION",
    )
    for phrase in required_phrases:
        check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")
    check("strategy index route", MANIFEST.name in index_text and CERTIFICATE.name in index_text and CANDIDATE_ID in index_text, [MANIFEST.name in index_text, CERTIFICATE.name in index_text, CANDIDATE_ID in index_text], [True, True, True], "certificate")
    check("prior art boundary denies world-first", "No world-first or new general PDE theorem is claimed" in certificate_text, "No world-first or new general PDE theorem is claimed" in certificate_text, True, "certificate")
    check("manifest physical predictions empty", manifest["input_prediction_accounting"]["physical_predictions"] == [], manifest["input_prediction_accounting"]["physical_predictions"], [], "certificate")
    check("manifest holdout false", manifest["input_prediction_accounting"]["holdout_prediction"] is False, manifest["input_prediction_accounting"]["holdout_prediction"], False, "certificate")


    with tempfile.TemporaryDirectory(prefix="tect-cl8-global-goursat-pdf-") as directory:
        temporary = Path(directory)
        rebuilt_pdf = temporary / "rebuilt.pdf"
        built = subprocess.run(
            [sys.executable, str(PDF_BUILDER), "--output", str(rebuilt_pdf)],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
        check(
            "deterministic canonical PDF rebuild",
            built.returncode == 0 and not built.stderr.strip() and sha256(rebuilt_pdf) == sha256(PDF),
            (built.returncode, built.stderr.strip(), sha256(rebuilt_pdf)),
            (0, "", sha256(PDF)),
            "pdf",
        )
        with pdfplumber.open(PDF) as document:
            page_texts = [(page.extract_text() or "") for page in document.pages]
            page_sizes = [(round(page.width, 3), round(page.height, 3)) for page in document.pages]
        combined_text = "\n".join(page_texts)
        check(
            "PDF pages nonblank and A4",
            len(page_texts) > 0 and all(item.strip() for item in page_texts) and len(set(page_sizes)) == 1 and page_sizes[0] == (595.276, 841.89),
            (len(page_texts), page_sizes),
            "positive nonblank pages with one A4 box",
            "pdf",
        )
        reader = PdfReader(PDF)
        root = reader.trailer["/Root"]
        active_keys = ("/AcroForm", "/Names", "/OpenAction", "/AA", "/JavaScript")
        check(
            "PDF security surface inert",
            not reader.is_encrypted and all(key not in root for key in active_keys),
            {"encrypted": reader.is_encrypted, "active_keys": [key for key in active_keys if key in root]},
            {"encrypted": False, "active_keys": []},
            "pdf",
        )
        proof_tokens = (CANDIDATE_ID, RESULT_ID, "Bielecki", "first contact", "D_(m-1)", "CP1 and Pre-A remain open")
        check(
            "PDF canonical proof and no-overclaim anchors",
            all(token in combined_text for token in proof_tokens),
            {token: token in combined_text for token in proof_tokens},
            {token: True for token in proof_tokens},
            "pdf",
        )
        renderer = find_pdftoppm()
        render_prefix = temporary / "page"
        rendered = subprocess.run(
            [str(renderer), "-png", "-r", "120", str(PDF), str(render_prefix)],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
        images = sorted(temporary.glob("page-*.png"))
        dimensions: list[tuple[int, int]] = []
        extrema: list[tuple[int, int]] = []
        for image_path in images:
            with Image.open(image_path) as raster:
                dimensions.append(raster.size)
                grayscale = raster.convert("L")
                extrema.append(grayscale.getextrema())
                ImageStat.Stat(grayscale).mean
        font_pages = [bool((page.get("/Resources") or {}).get("/Font")) for page in reader.pages]
        check(
            "Poppler all-page render surface",
            rendered.returncode == 0 and len(images) == len(page_texts) and len(set(dimensions)) == 1 and all(low < 245 and high == 255 for low, high in extrema) and all(font_pages),
            {"returncode": rendered.returncode, "page_count": len(images), "dimensions": dimensions, "extrema": extrema, "font_resources": font_pages},
            "every page rendered, nonblank, same-sized, and font-backed",
            "pdf",
        )
        pdf_qa_manifest = manifest["pdf_qa"]
        check(
            "PDF manifest pin and manual visual QA",
            pdf_qa_manifest["path"] == str(PDF.relative_to(REPO)).replace("\\", "/")
            and pdf_qa_manifest["sha256"] == sha256(PDF)
            and pdf_qa_manifest["page_count"] == len(page_texts)
            and pdf_qa_manifest["manual_visual_qa"].startswith("PASS:"),
            pdf_qa_manifest,
            {"path": str(PDF.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(PDF), "page_count": len(page_texts), "manual_visual_qa": "PASS: ..."},
            "pdf",
        )

    if len(rows) != EXPECTED_INTEGRATED_ASSERTIONS:
        raise AssertionError(f"integrated assertion surface drifted: {len(rows)} != {EXPECTED_INTEGRATED_ASSERTIONS}")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "version": __version__,
        "issued": "2026-08-03",
        "version_issued": __version_issued__,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "child_assertions": {
            "primary": EXPECTED_PRIMARY_ASSERTIONS,
            "independent": EXPECTED_INDEPENDENT_ASSERTIONS,
        },
        "total_verified_assertions": EXPECTED_PRIMARY_ASSERTIONS + EXPECTED_INDEPENDENT_ASSERTIONS + EXPECTED_INTEGRATED_ASSERTIONS,
        "authority_sha256": authority_hashes,
        "source_sha256": {
            "verifier": sha256(VERIFIER),
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "pdf_builder": sha256(PDF_BUILDER),
            "pdf": sha256(PDF),
        },
        "scope": scope,
        "pdf_qa": {"path": str(PDF.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(PDF), "page_count": len(PdfReader(PDF).pages), "renderer": str(find_pdftoppm()).replace("\\", "/"), "manual_visual_qa": manifest["pdf_qa"]["manual_visual_qa"]},
        "assertions": rows,
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "next_gate": gate["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check-stored",
        action="store_true",
        help="compare a fresh integrated payload with the stored integrated artifact without overwriting it",
    )
    args = parser.parse_args()
    payload = verify()
    if args.check_stored:
        if not STORED_INTEGRATED.is_file():
            raise AssertionError(f"stored integrated artifact missing: {STORED_INTEGRATED}")
        stored = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored integrated artifact differs from fresh integrated payload")
        count = payload["assertion_summary"]["total"]
        print(f"{CANDIDATE_ID} stored integrated: {count}/{count} PASS")
        return 0
    atomic_json(args.output, payload)
    count = payload["assertion_summary"]["total"]
    print(f"{CANDIDATE_ID} integrated: {count}/{count} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
