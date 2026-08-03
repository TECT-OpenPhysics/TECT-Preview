#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0."""

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
CANDIDATE_ID = "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0"
RESULT_ID = "PA-CP1-CL8-FINITE-QUANTUM-GROUND-THERMAL-STATE-AND-BOUNDARY-FORK"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE"
SLUG = "pre-a-cp1-cl8-finite-quantum-state-boundary-fork"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / f"codes/foundations/pre_a_cp1_cl8_finite_quantum_state_boundary_fork.py"
INDEPENDENT_SCRIPT = REPO / f"codes/foundations/pre_a_cp1_cl8_finite_quantum_state_boundary_fork_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260803.md"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CLASSICAL_FORK = REPO / "strategy/pre-a-cp1-cl8-invariance-selection-fork-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
GAUSSIAN_CCR = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
PRIOR_ART = REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-integrated-{SLUG}/result.json"

# Exact regression oracles.  Any parent authority change requires a fresh audit,
# rather than silently allowing this certificate to inherit a changed premise.
EXPECTED_PRIMARY_ASSERTIONS = 79
EXPECTED_INDEPENDENT_ASSERTIONS = 90
EXPECTED_AUTHORITY_HASHES = {
    "semidiscrete_manifest": "1862badf2c4255de4cfaf12cf369a4c07a8a418275485789a08f7aa1d6d9864a",
    "q3lock_manifest": "d49686f88833f323beabd2953eb50d0a1083d3d71fcc28e27da6a4d2b3b81046",
    "classical_fork_manifest": "070131b3ede042840ba29757ad010f8ad0bb130dfc370b870d988360de57e34d",
    "global_manifest": "c2c0a5bc78a259c1116e68a31a41d251a0cb644956ffed3c583d786fdf1cb496",
    "gaussian_ccr_manifest": "a0aa2792f44eb04054237638cb2158143235a7f9ecd6e715b701fdb09007c021",
    "prior_art_matrix": "ff19065d22110c409ed9e3c5018e5357882a090de7a46035226e76637e606c5a",
    "c6_status": "a0d6d7cd99770cd97050eb28fc4dc69180191ba930de629ee023cffc3a2aa811",
}


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
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script.name}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    c6_status = load_json(C6_STATUS)
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    exploration_text = EXPLORATIONS.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
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

    with tempfile.TemporaryDirectory(prefix="tect-cl8-quantum-state-fork-") as directory:
        temporary = Path(directory)
        fresh_primary = run_child(PRIMARY_SCRIPT, temporary / "primary.json")
        fresh_independent = run_child(INDEPENDENT_SCRIPT, temporary / "independent.json")

    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    check("stored primary equals fresh", stored_primary == fresh_primary, sha256(PRIMARY_RESULT), "fresh primary payload", "freshness")
    check("stored independent equals fresh", stored_independent == fresh_independent, sha256(INDEPENDENT_RESULT), "fresh independent payload", "freshness")
    check("primary exact assertion count", fresh_primary["assertion_summary"] == {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, fresh_primary["assertion_summary"], {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, "children")
    check("independent exact assertion count", fresh_independent["assertion_summary"] == {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, fresh_independent["assertion_summary"], {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, "children")
    for child_name, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        check(f"{child_name} identity", child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID, [child["candidate_id"], child["result_id"]], [CANDIDATE_ID, RESULT_ID], "children")
        check(f"{child_name} nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "children")
    check("derived structures agree", fresh_primary["derived"] == fresh_independent["derived"], fresh_primary["derived"], fresh_independent["derived"], "cross")
    check("scope structures agree", fresh_primary["scope"] == fresh_independent["scope"] == manifest["scope"], [fresh_primary["scope"], fresh_independent["scope"]], manifest["scope"], "cross")
    check("verdict structures agree", fresh_primary["verdict"] == fresh_independent["verdict"] == manifest["verdict"], [fresh_primary["verdict"], fresh_independent["verdict"]], manifest["verdict"], "cross")
    check("next gate structures agree", fresh_primary["next_gate"] == fresh_independent["next_gate"] == manifest["gate_resolution"]["next_gate"], [fresh_primary["next_gate"], fresh_independent["next_gate"]], manifest["gate_resolution"]["next_gate"], "cross")

    check("primary script hash fresh", fresh_primary["source_sha256"]["script"] == sha256(PRIMARY_SCRIPT), fresh_primary["source_sha256"]["script"], sha256(PRIMARY_SCRIPT), "provenance")
    check("independent script hash fresh", fresh_independent["source_sha256"]["script"] == sha256(INDEPENDENT_SCRIPT), fresh_independent["source_sha256"]["script"], sha256(INDEPENDENT_SCRIPT), "provenance")
    check("primary manifest hash fresh", fresh_primary["source_sha256"]["manifest"] == sha256(MANIFEST), fresh_primary["source_sha256"]["manifest"], sha256(MANIFEST), "provenance")
    check("independent manifest hash fresh", fresh_independent["source_sha256"]["manifest"] == sha256(MANIFEST), fresh_independent["source_sha256"]["manifest"], sha256(MANIFEST), "provenance")
    authority_paths = {
        "semidiscrete_manifest": SEMIDISCRETE,
        "q3lock_manifest": Q3LOCK,
        "classical_fork_manifest": CLASSICAL_FORK,
        "global_manifest": GLOBAL,
        "gaussian_ccr_manifest": GAUSSIAN_CCR,
        "prior_art_matrix": PRIOR_ART,
        "c6_status": C6_STATUS,
    }
    authority_hashes = {name: sha256(path) for name, path in authority_paths.items()}
    for name, expected in EXPECTED_AUTHORITY_HASHES.items():
        check(f"authority hash pinned: {name}", authority_hashes[name] == expected, authority_hashes[name], expected, "provenance")
    for child_name, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        for name in ("semidiscrete_manifest", "q3lock_manifest", "classical_fork_manifest", "global_manifest", "gaussian_ccr_manifest", "prior_art_matrix"):
            check(f"{child_name} parent hash: {name}", child["source_sha256"][name] == authority_hashes[name], child["source_sha256"][name], authority_hashes[name], "provenance")

    check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    check("manifest T0 nonbearing", manifest["claim_bearing"] is False and manifest["authority"].startswith("T0"), [manifest["claim_bearing"], manifest["authority"]], [False, "T0..."], "manifest")
    check("manifest negative", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "manifest")
    check("one closed subgate", manifest["gate_resolution"]["closed_subgate"] == "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-GROUND-AND-GIBBS-STATE", manifest["gate_resolution"]["closed_subgate"], "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-GROUND-AND-GIBBS-STATE", "manifest")
    check("one refuted subgate", manifest["gate_resolution"]["refuted_subgate"] == "PA-CP1-CL8-STATIONARITY-AND-SYMMETRY-ONLY-QUANTUM-PREFERENCE", manifest["gate_resolution"]["refuted_subgate"], "PA-CP1-CL8-STATIONARITY-AND-SYMMETRY-ONLY-QUANTUM-PREFERENCE", "manifest")
    check("four open successors", len(manifest["gate_resolution"]["open_subgates"]) == 4, manifest["gate_resolution"]["open_subgates"], "four", "manifest")
    check("parent state gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "manifest")
    check("normal state algebra exact", manifest["state_algebra"]["observable_algebra"].startswith("B(H_a)") and "infinite-dimensional" in manifest["state_algebra"]["observable_algebra"], manifest["state_algebra"]["observable_algebra"], "B(H_a), infinite-dimensional Hilbert space", "manifest")
    check("interacting Weyl dynamics kept open", "not proved" in manifest["state_algebra"]["dynamics_boundary"], manifest["state_algebra"]["dynamics_boundary"], "not proved", "manifest")
    check("coarse translation only", "fine one-site ST8 translation is not claimed" in manifest["coercive_operator_theorem"]["symmetry"], manifest["coercive_operator_theorem"]["symmetry"], "fine one-site symmetry excluded", "manifest")
    check("lambda-zero minimum boundary", "lambda=0 has a larger sign-minimum set" in manifest["coercive_operator_theorem"]["finite_volume_boundary"], manifest["coercive_operator_theorem"]["finite_volume_boundary"], "lambda=0 boundary", "manifest")
    check("Pre-A role bounded", "not established" in manifest["Pre_A_chain_role"]["N1_boundary"] and "neither closes C0" in manifest["Pre_A_chain_role"]["chain_verdict"], manifest["Pre_A_chain_role"], "not N1 and not C0/N1-N5 closure", "manifest")

    expected_derived = {
        "dimension": "8*M",
        "weight": "a/8",
        "canonical_momentum": "p=(a/8)*Pi",
        "kappa": "4*hbar^2/(a*chi)",
        "A": "a*g/(32*d)",
        "B": "a*r_minus/16",
        "C_mu": "(B+mu)^2/(4*A)",
        "cutoff_scaling": "L*g/(256*M^2)",
        "thermal_weights": ["4/7", "2/7", "1/7"],
        "thermal_purity": "3/7",
        "operator_shift": "L*C_star/8=L*r_minus^2/(4*g)",
        "negative": NEGATIVE_ID,
    }
    derived = fresh_primary["derived"]
    actual_derived = {
        "dimension": derived["dimensions"]["configuration"],
        "weight": derived["quantization"]["weight"],
        "canonical_momentum": derived["quantization"]["canonical_momentum"],
        "kappa": derived["quantization"]["kappa"],
        "A": derived["coercivity"]["A"],
        "B": derived["coercivity"]["B"],
        "C_mu": derived["coercivity"]["C_mu"],
        "cutoff_scaling": derived["coercivity"]["cutoff_scaling"],
        "thermal_weights": derived["spectral_fixture"]["thermal_weights"],
        "thermal_purity": derived["spectral_fixture"]["thermal_purity"],
        "operator_shift": derived["shift"]["operator"],
        "negative": derived["negative_id"],
    }
    check("load-bearing derived values", actual_derived == expected_derived, actual_derived, expected_derived, "mathematics")
    check("exact fixture constants", derived["fixture"] == {"A": "1/1024", "B": "3/32", "C_mu": "4", "d": 32, "kappa": "36", "s0": "64", "weight": "1/16"}, derived["fixture"], "exact fixture", "mathematics")
    check("spectral witnesses distinct", derived["spectral_fixture"]["distinct"] is True and derived["spectral_fixture"]["stationary"] is True and derived["spectral_fixture"]["symmetric"] is True, derived["spectral_fixture"], "distinct stationary symmetric witnesses", "mathematics")
    check("normalized states shift invariant", derived["shift"]["normalized_states_unchanged"] is True and derived["shift"]["fixture"] == "9/4", derived["shift"], "invariant with fixture 9/4", "mathematics")

    anchors = (
        'id="section-1-verdict"',
        'id="section-3-canonical-variables"',
        'id="section-4-coercive-form"',
        'id="section-5-ground-state"',
        'id="section-6-thermal-states"',
        'id="section-7-selection-no-go"',
        'id="section-8-energy-shift"',
        'id="section-9-boundary-fork"',
        'id="section-10-adversarial"',
        'id="section-12-no-overclaim"',
    )
    for anchor in anchors:
        check(f"certificate anchor: {anchor}", anchor in certificate_text, anchor in certificate_text, True, "certificate")
    phrases = (
        "p=(a/8)Pi",
        "4\\hbar^2\\over a\\chi",
        "compact resolvent by itself is not enough".capitalize(),
        NEGATIVE_ID,
        "configuration marginal",
        "not cutoff uniform",
        "physical empty space",
        "and Pre-A remain open",
    )
    for phrase in phrases:
        check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")
    check("prior art bounded", "not a new general operator theorem" in certificate_text and "no world-first" in manifest["prior_art_boundary"].lower(), ["not a new general operator theorem" in certificate_text, "no world-first" in manifest["prior_art_boundary"].lower()], [True, True], "certificate")

    check("formal negative in summary table", f"[{NEGATIVE_ID}]" in registry_text, f"[{NEGATIVE_ID}]" in registry_text, True, "records")
    check("formal negative section", f"### {NEGATIVE_ID}" in registry_text, f"### {NEGATIVE_ID}" in registry_text, True, "records")
    check("formal negative evidence path", SLUG in registry_text, SLUG in registry_text, True, "records")
    check("exploration decision present", '"id":"EXP-000738"' in exploration_text and NEGATIVE_ID in exploration_text, ['"id":"EXP-000738"' in exploration_text, NEGATIVE_ID in exploration_text], [True, True], "records")
    check("strategy index row", f"{SLUG}-manifest.json" in index_text, f"{SLUG}-manifest.json" in index_text, True, "records")

    check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    check("C6 tier unchanged", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    check("C6 lifecycle unchanged", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    check("C6 evidence unchanged", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    check("C6 gate unchanged", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    required_true = (
        "finite_quantum_CCR_declared",
        "finite_quantum_self_adjoint_operator",
        "finite_quantum_compact_resolvent",
        "finite_quantum_unique_ground",
        "finite_quantum_thermal_Gibbs",
        "ground_selected_given_criterion",
    )
    for key in required_true:
        check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    required_false = (
        "stationarity_only_unique_preference",
        "hbar_origin_derived",
        "physical_state_criterion_derived",
        "pure_ordered_finite_phase",
        "quantum_boundary_algebra_map",
        "quantum_characteristic_state",
        "continuum_quantum_state",
        "Hadamard_state",
        "cutoff_uniform_trace_bound",
        "thermodynamic_limit",
        "physical_vacuum",
        "below_empty_space",
        "full_3_plus_1_dependence",
        "gravity",
        "cooling",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

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
        "derived": derived,
        "scope": manifest["scope"],
        "assertions": rows,
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary_script": sha256(PRIMARY_SCRIPT),
            "independent_script": sha256(INDEPENDENT_SCRIPT),
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
