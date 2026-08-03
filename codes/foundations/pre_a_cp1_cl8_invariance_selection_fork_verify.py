#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-CL8-INVARIANCE-SELECTION-FORK-v0."""

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
CANDIDATE_ID = "PA-CP1-CL8-INVARIANCE-SELECTION-FORK-v0"
RESULT_ID = "PA-CP1-CL8-FINITE-GIBBS-AND-COMMON-EQUILIBRIUM-MEASURE-FORK"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE"
SLUG = "pre-a-cp1-cl8-invariance-selection-fork"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / f"codes/foundations/pre_a_cp1_cl8_invariance_selection_fork.py"
INDEPENDENT_SCRIPT = REPO / f"codes/foundations/pre_a_cp1_cl8_invariance_selection_fork_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260803.md"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_PRIMARY_ASSERTIONS = 59
EXPECTED_INDEPENDENT_ASSERTIONS = 66
EXPECTED_AUTHORITY_HASHES = {
    "semidiscrete_manifest": "1862badf2c4255de4cfaf12cf369a4c07a8a418275485789a08f7aa1d6d9864a",
    "q3lock_manifest": "d49686f88833f323beabd2953eb50d0a1083d3d71fcc28e27da6a4d2b3b81046",
    "global_manifest": "c2c0a5bc78a259c1116e68a31a41d251a0cb644956ffed3c583d786fdf1cb496",
    "composition_manifest": "6f046b62c99c43ac6c04de546669f635cfb079c3c5ecad5e09bb7e6674a8d0b6",
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

    with tempfile.TemporaryDirectory(prefix="tect-cl8-state-fork-") as directory:
        temporary = Path(directory)
        fresh_primary = run_child(PRIMARY_SCRIPT, temporary / "primary.json")
        fresh_independent = run_child(INDEPENDENT_SCRIPT, temporary / "independent.json")

    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    check("stored primary equals fresh", stored_primary == fresh_primary, sha256(PRIMARY_RESULT), "fresh primary payload", "freshness")
    check("stored independent equals fresh", stored_independent == fresh_independent, sha256(INDEPENDENT_RESULT), "fresh independent payload", "freshness")
    check("primary exact assertion count", fresh_primary["assertion_summary"] == {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, fresh_primary["assertion_summary"], {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, "children")
    check("independent exact assertion count", fresh_independent["assertion_summary"] == {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, fresh_independent["assertion_summary"], {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, "children")
    check("primary identity", fresh_primary["candidate_id"] == CANDIDATE_ID and fresh_primary["result_id"] == RESULT_ID, [fresh_primary["candidate_id"], fresh_primary["result_id"]], [CANDIDATE_ID, RESULT_ID], "children")
    check("independent identity", fresh_independent["candidate_id"] == CANDIDATE_ID and fresh_independent["result_id"] == RESULT_ID, [fresh_independent["candidate_id"], fresh_independent["result_id"]], [CANDIDATE_ID, RESULT_ID], "children")
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
        "global_manifest": GLOBAL,
        "composition_manifest": COMPOSITION,
        "c6_status": C6_STATUS,
    }
    authority_hashes = {name: sha256(path) for name, path in authority_paths.items()}
    for name, expected in EXPECTED_AUTHORITY_HASHES.items():
        check(f"authority hash pinned: {name}", authority_hashes[name] == expected, authority_hashes[name], expected, "provenance")
    for child_name, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        for name in ("semidiscrete_manifest", "q3lock_manifest", "global_manifest", "composition_manifest"):
            check(f"{child_name} parent hash: {name}", child["source_sha256"][name] == authority_hashes[name], child["source_sha256"][name], authority_hashes[name], "provenance")

    check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    check("manifest T0 nonbearing", manifest["claim_bearing"] is False and manifest["authority"].startswith("T0"), [manifest["claim_bearing"], manifest["authority"]], [False, "T0..."], "manifest")
    check("manifest negative", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "manifest")
    check("two closed subgates", len(manifest["gate_resolution"]["closed_subgates"]) == 2, manifest["gate_resolution"]["closed_subgates"], "two", "manifest")
    check("one refuted subgate", manifest["gate_resolution"]["refuted_subgate"] == "PA-CP1-CL8-INVARIANCE-AND-SYMMETRY-ONLY-PREFERRED-MEASURE", manifest["gate_resolution"]["refuted_subgate"], "PA-CP1-CL8-INVARIANCE-AND-SYMMETRY-ONLY-PREFERRED-MEASURE", "manifest")
    check("five open successors", len(manifest["gate_resolution"]["open_subgates"]) == 5, manifest["gate_resolution"]["open_subgates"], "five", "manifest")
    check("parent state gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "manifest")

    expected_derived = {
        "beta_domain": "beta>0",
        "variance": "8*chi/(beta*a)",
        "zero_error": 0,
        "negative": NEGATIVE_ID,
    }
    actual_derived = {
        "beta_domain": fresh_primary["derived"]["Gibbs"]["beta_domain"],
        "variance": fresh_primary["derived"]["Gibbs"]["momentum_variance"],
        "zero_error": fresh_primary["derived"]["witnesses"]["composition_error"],
        "negative": fresh_primary["derived"]["negative_id"],
    }
    check("load-bearing derived values", actual_derived == expected_derived, actual_derived, expected_derived, "mathematics")
    check("exact weak floor constants", fresh_primary["derived"]["coercivity"] == {"weak_constant": "L*r_minus^2/(2*g)", "exact_floor": "-L*r_minus^2/(4*g)", "weak_square": "(g*z^2-2*r_minus)^2/(8*g)"}, fresh_primary["derived"]["coercivity"], "exact constants", "mathematics")
    check("Liouville identities zero", set(fresh_primary["derived"]["Liouville"].values()) == {"0"}, fresh_primary["derived"]["Liouville"], {"all": "0"}, "mathematics")
    check("witnesses distinct", fresh_primary["derived"]["witnesses"]["distinct"] is True and fresh_primary["derived"]["witnesses"]["ordered_second_moment"] == "-r/g", fresh_primary["derived"]["witnesses"], "distinct with ordered moment -r/g", "mathematics")

    anchors = (
        'id="section-1-verdict"',
        'id="section-3-finite-hamiltonian"',
        'id="section-4-coercivity"',
        'id="section-5-liouville-gibbs"',
        'id="section-6-common-witnesses"',
        'id="section-7-no-go"',
        'id="section-8-composition-boundary"',
        'id="section-10-adversarial"',
        'id="section-12-no-overclaim"',
    )
    for anchor in anchors:
        check(f"certificate anchor: {anchor}", anchor in certificate_text, anchor in certificate_text, True, "certificate")
    phrases = (
        "8\\chi\\over\\beta a",
        "exactly zero",
        NEGATIVE_ID,
        "autonomous invariance",
        "not a density operator",
        "physical empty space",
        "CP1, or Pre-A",
    )
    for phrase in phrases:
        check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")
    check("prior art bounded", "not a new general theorem" in certificate_text and "no world-first" in manifest["prior_art_boundary"].lower(), ["not a new general theorem" in certificate_text, "no world-first" in manifest["prior_art_boundary"].lower()], [True, True], "certificate")

    check("formal negative in summary table", f"[{NEGATIVE_ID}]" in registry_text, f"[{NEGATIVE_ID}]" in registry_text, True, "records")
    check("formal negative section", f"### {NEGATIVE_ID}" in registry_text, f"### {NEGATIVE_ID}" in registry_text, True, "records")
    check("formal negative evidence path", SLUG in registry_text, SLUG in registry_text, True, "records")
    check("corrected exploration inherited", '"id":"EXP-000735"' in exploration_text and '"relation":"corrects"' in exploration_text, ['"id":"EXP-000735"' in exploration_text, '"relation":"corrects"' in exploration_text], [True, True], "records")
    check("strategy index row", f"{SLUG}-manifest.json" in index_text, f"{SLUG}-manifest.json" in index_text, True, "records")

    check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    check("C6 tier unchanged", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    check("C6 lifecycle unchanged", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    check("C6 evidence unchanged", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    check("C6 gate unchanged", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    required_false = (
        "invariance_only_unique_preference",
        "derived_beta_or_energy",
        "selected_physical_classical_measure",
        "finite_quantum_state",
        "quantum_boundary_state",
        "continuum_quantum_state",
        "Hadamard_state",
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

    payload = {
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
    return payload


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
