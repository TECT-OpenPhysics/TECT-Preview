#!/usr/bin/env python3
"""Integrated verifier for the CL8 quantum boundary-algebra route split."""

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
CANDIDATE_ID = "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-ORDERED-TANGENT-FINITE-IMAGE-WEYL-STATE-PULLBACK-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / "codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split.py"
INDEPENDENT_SCRIPT = REPO / "codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GAUSSIAN = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
CLASSICAL = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
QUANTUM = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
PRIOR_ART = REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
PRIMARY_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)
INDEPENDENT_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-integrated-{SLUG}/result.json"
)
EXPECTED_PRIMARY_ASSERTIONS = 93
EXPECTED_INDEPENDENT_ASSERTIONS = 87
EXPECTED_PARENT_IDS = [
    "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
    "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
]


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script.name}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return load_json(output)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def build_payload() -> dict[str, Any]:
    audit = Audit()
    required_files = (
        PRIMARY_SCRIPT,
        INDEPENDENT_SCRIPT,
        MANIFEST,
        CERTIFICATE,
        GLOBAL,
        Q3LOCK,
        GAUSSIAN,
        CLASSICAL,
        QUANTUM,
        PRIOR_ART,
        C6_STATUS,
        NEGATIVE_REGISTRY,
        EXPLORATIONS,
        STRATEGY_INDEX,
        PRIMARY_RESULT,
        INDEPENDENT_RESULT,
    )
    for path in required_files:
        audit.check(f"required file: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = load_json(MANIFEST)
    c6_status = load_json(C6_STATUS)
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    exploration_text = EXPLORATIONS.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="tect-cl8-boundary-route-split-") as directory:
        temporary = Path(directory)
        fresh_primary = run_child(PRIMARY_SCRIPT, temporary / "primary.json")
        fresh_independent = run_child(INDEPENDENT_SCRIPT, temporary / "independent.json")
    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    audit.check("stored primary equals fresh", stored_primary == fresh_primary, sha256(PRIMARY_RESULT), "fresh primary payload", "freshness")
    audit.check("stored independent equals fresh", stored_independent == fresh_independent, sha256(INDEPENDENT_RESULT), "fresh independent payload", "freshness")
    audit.check("primary exact count", fresh_primary["assertion_summary"] == {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, fresh_primary["assertion_summary"], {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, "children")
    audit.check("independent exact count", fresh_independent["assertion_summary"] == {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, fresh_independent["assertion_summary"], {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, "children")
    for label, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        audit.check(f"{label} identity", child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID, [child["candidate_id"], child["result_id"]], [CANDIDATE_ID, RESULT_ID], "children")
        audit.check(f"{label} claim nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "children")
        audit.check(f"{label} all assertions pass", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "children")
    audit.check("independent derived agreement", fresh_primary["derived"] == fresh_independent["derived"], fresh_primary["derived"], fresh_independent["derived"], "cross")
    audit.check("independent scope agreement", fresh_primary["scope"] == fresh_independent["scope"] == manifest["scope"], [fresh_primary["scope"], fresh_independent["scope"]], manifest["scope"], "cross")
    audit.check("independent negative agreement", fresh_primary["negative_ids"] == fresh_independent["negative_ids"], fresh_primary["negative_ids"], fresh_independent["negative_ids"], "cross")
    audit.check("independent verdict agreement", fresh_primary["verdict"] == fresh_independent["verdict"] == manifest["verdict"], [fresh_primary["verdict"], fresh_independent["verdict"]], manifest["verdict"], "cross")
    audit.check("independent next gate agreement", fresh_primary["next_gate"] == fresh_independent["next_gate"] == manifest["gate_resolution"]["next_gate"], [fresh_primary["next_gate"], fresh_independent["next_gate"]], manifest["gate_resolution"]["next_gate"], "cross")

    authority_paths = {
        "global_manifest": GLOBAL,
        "q3lock_manifest": Q3LOCK,
        "gaussian_manifest": GAUSSIAN,
        "classical_manifest": CLASSICAL,
        "quantum_manifest": QUANTUM,
    }
    authority_hashes = {name: sha256(path) for name, path in authority_paths.items()}
    for label, child, script in (
        ("primary", fresh_primary, PRIMARY_SCRIPT),
        ("independent", fresh_independent, INDEPENDENT_SCRIPT),
    ):
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(script), child["source_sha256"]["script"], sha256(script), "provenance")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "provenance")
        for name, expected in authority_hashes.items():
            audit.check(f"{label} authority hash: {name}", child["source_sha256"][name] == expected, child["source_sha256"][name], expected, "provenance")

    audit.check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest T0 nonbearing", manifest["authority"].startswith("T0") and manifest["claim_bearing"] is False, [manifest["authority"], manifest["claim_bearing"]], ["T0...", False], "manifest")
    audit.check("manifest exact parents", manifest["parent_ids"] == EXPECTED_PARENT_IDS, manifest["parent_ids"], EXPECTED_PARENT_IDS, "manifest")
    audit.check("manifest algebra direction", manifest["algebra_contract"]["map_direction"].startswith("alpha_a:"), manifest["algebra_contract"]["map_direction"], "alpha_a boundary to bulk", "manifest")
    audit.check("manifest algebra distinction", "not interchanged" in manifest["algebra_contract"]["B_of_H_boundary"], manifest["algebra_contract"]["B_of_H_boundary"], "not interchanged", "manifest")
    audit.check("manifest restricted regulator", manifest["restricted_sampling_theorem"]["regulator"] == "even M>=4, a=L/M, periodic nodes x_j=j*a", manifest["restricted_sampling_theorem"]["regulator"], "even M>=4", "manifest")
    audit.check("manifest actual state pullback", "actual interacting ground or Gibbs density" in manifest["interacting_state_pullback"]["interaction_status"], manifest["interacting_state_pullback"]["interaction_status"], "actual interacting ground or Gibbs density", "manifest")
    audit.check("manifest parent open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "manifest")
    audit.check("manifest three closed", len(manifest["gate_resolution"]["closed_subgates"]) == 3, manifest["gate_resolution"]["closed_subgates"], "three", "manifest")
    audit.check("manifest three refuted", len(manifest["gate_resolution"]["refuted_subgates"]) == 3, manifest["gate_resolution"]["refuted_subgates"], "three", "manifest")
    audit.check("manifest conditional N1 only", "N1 is not closed" in manifest["Pre_A_chain_role"]["N1"], manifest["Pre_A_chain_role"]["N1"], "N1 is not closed", "manifest")
    audit.check("manifest no world first", "No world-first" in manifest["prior_art_boundary"], manifest["prior_art_boundary"], "No world-first", "manifest")

    expected_derived = {
        "M_fixture": 4,
        "continuum_frequency_squared": 25,
        "continuum_gram": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
        "discrete_gram": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
        "frequencies": [3, 5, 5],
        "lattice_fixture_frequency_squared": "9 + 128/pi^2",
        "moyal_discrepancy": "hbar^2/3",
        "moyal_lambda3": [36, -12],
        "next_gate": "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL",
        "nonlinear_Pi_third": "-3*g*tau",
        "nonlinear_q_third": "-3*g*tau^2/(2*chi)",
        "ordered_q_second_endpoint_slope": "-3*g*v0*tau/chi",
        "sampling_kernel_sigma": "L/16",
        "sampling_rank": 6,
        "scaled_commutator": "-1",
        "shear_additivity_defect": ["0", "2*gamma"],
        "transfer_determinants": ["1", "1", "1"],
    }
    audit.check("load-bearing derived values", fresh_primary["derived"] == expected_derived, fresh_primary["derived"], expected_derived, "mathematics")

    anchors = (
        'id="section-1-verdict"',
        'id="section-2-authorities-and-sign"',
        'id="section-3-ordered-tangent"',
        'id="section-4-characteristic-image"',
        'id="section-5-restricted-sampling"',
        'id="section-6-state-pullback"',
        'id="section-7-sampling-no-go"',
        'id="section-8-nonlinear-relabel-no-go"',
        'id="section-9-dynamics-no-go"',
        'id="section-10-groenewold-boundary"',
        'id="section-11-gate-and-chain"',
        'id="section-12-adversarial-review"',
        'id="section-14-no-overclaim"',
    )
    for anchor in anchors:
        audit.check(f"certificate anchor: {anchor}", anchor in certificate_text, anchor in certificate_text, True, "certificate")
    phrases = (
        "sigma=-Omega_var",
        "P_\\tau T=S_\\tau",
        "omega_{H,a}=\\omega_a\\circ\\alpha_a",
        "source Weyl commutator",
        "not an exact dynamics intertwiner",
        "hbar^2 I/3",
        "N1 gains a conditional cutoff finite-image ingredient",
        "and does not complete Pre-A",
    )
    for phrase in phrases:
        audit.check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")

    negative_ids = fresh_primary["negative_ids"]
    for negative_id in negative_ids:
        anchor = negative_id.lower()
        audit.check(f"negative summary: {negative_id}", f"[{negative_id}]" in registry_text, f"[{negative_id}]" in registry_text, True, "records")
        audit.check(f"negative section: {negative_id}", f"### {negative_id}" in registry_text, f"### {negative_id}" in registry_text, True, "records")
        audit.check(f"negative anchor: {negative_id}", f'id="{anchor}"' in registry_text, f'id="{anchor}"' in registry_text, True, "records")
    audit.check("exploration record", '"id":"EXP-000741"' in exploration_text, '"id":"EXP-000741"' in exploration_text, True, "records")
    audit.check("exploration correction", '"id":"EXP-000742"' in exploration_text and '"relation":"corrects"' in exploration_text, ['"id":"EXP-000742"' in exploration_text, '"relation":"corrects"' in exploration_text], [True, True], "records")
    for negative_id in negative_ids:
        audit.check(f"exploration formal negative: {negative_id}", negative_id in exploration_text, negative_id in exploration_text, True, "records")
    audit.check("strategy index row", f"{SLUG}-manifest.json" in index_text, f"{SLUG}-manifest.json" in index_text, True, "records")

    audit.check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    audit.check("C6 tier unchanged", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    audit.check("C6 lifecycle unchanged", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    audit.check("C6 evidence unchanged", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    audit.check("C6 gate unchanged", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    required_true = (
        "ordered_tangent_finite_image_symplectic_isomorphism",
        "finite_image_metaplectic_control",
        "restricted_finite_a_Weyl_monomorphism",
        "interacting_bulk_state_restricted_boundary_pullback",
        "conditional_N1_cutoff_ingredient",
    )
    for key in required_true:
        audit.check(f"integrated scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    required_false = (
        "unrestricted_point_sampling_exact_Weyl",
        "direct_nonlinear_generator_relabel_Weyl",
        "current_sampling_exact_dynamics_intertwiner",
        "full_finite_a_boundary_algebra",
        "interacting_boundary_bulk_dynamics_intertwiner",
        "interacting_Weyl_Cstar_dynamics_preserved",
        "preferred_physical_state_selected",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "physical_vacuum",
        "below_empty_space",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "full_3_plus_1_dependence",
        "gravity",
        "cooling",
        "cycle",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"integrated scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "child_assertion_counts": {
            "primary": EXPECTED_PRIMARY_ASSERTIONS,
            "independent": EXPECTED_INDEPENDENT_ASSERTIONS,
        },
        "child_result_sha256": {
            "primary": sha256(PRIMARY_RESULT),
            "independent": sha256(INDEPENDENT_RESULT),
        },
        "authority_sha256": authority_hashes,
        "derived": fresh_primary["derived"],
        "scope": manifest["scope"],
        "negative_ids": negative_ids,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary_script": sha256(PRIMARY_SCRIPT),
            "independent_script": sha256(INDEPENDENT_SCRIPT),
            "prior_art_matrix": sha256(PRIOR_ART),
            "c6_status": sha256(C6_STATUS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-stored", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.check_stored:
        stored = load_json(args.output)
        if stored != serial(payload):
            raise AssertionError("stored integrated result differs from fresh payload")
        summary = payload["assertion_summary"]
        print(f"{CANDIDATE_ID} stored integrated: {summary['passed']}/{summary['total']} PASS")
        return 0
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} integrated: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
