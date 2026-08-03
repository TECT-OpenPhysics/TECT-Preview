#!/usr/bin/env python3
"""Integrated verifier for the CL8 common-regulator characteristic route split."""

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
CANDIDATE_ID = "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-CAUSAL-CAUCHY-FLOQUET-BH-STATE-TRANSPORT-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / "codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py"
INDEPENDENT_SCRIPT = REPO / "codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
STRICT_CONE = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
QUANTUM_STATE = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
BOUNDARY_SPLIT = REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json"
PRIOR_ART = REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
TODO_JSON = REPO / "todo/todo.json"
CHANGELOG_JSONL = REPO / "changelog/log.jsonl"
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
EXPECTED_PRIMARY_ASSERTIONS = 120
EXPECTED_INDEPENDENT_ASSERTIONS = 99
EXPECTED_PARENT_IDS = [
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
    "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script.name}\nstdout={completed.stdout}\nstderr={completed.stderr}")
    return load_json(output)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def build_payload() -> dict[str, Any]:
    audit = Audit()
    parent_paths = (Q3LOCK, SEMIDISCRETE, STRICT_CONE, QUANTUM_STATE, BOUNDARY_SPLIT)
    required_files = (
        PRIMARY_SCRIPT,
        INDEPENDENT_SCRIPT,
        MANIFEST,
        CERTIFICATE,
        *parent_paths,
        PRIOR_ART,
        C6_STATUS,
        NEGATIVE_REGISTRY,
        EXPLORATIONS,
        STRATEGY_INDEX,
        TODO_JSON,
        CHANGELOG_JSONL,
        PRIMARY_RESULT,
        INDEPENDENT_RESULT,
    )
    for path in required_files:
        audit.check(f"required file: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = load_json(MANIFEST)
    c6_status = load_json(C6_STATUS)
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    todo_data = load_json(TODO_JSON)
    changelog_records = [json.loads(line) for line in CHANGELOG_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_records = [json.loads(line) for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines() if line.strip()]

    with tempfile.TemporaryDirectory(prefix="tect-cl8-common-circuit-") as directory:
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
        audit.check(f"{label} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "children")
        audit.check(f"{label} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "children")
        audit.check(f"{label} claim nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "children")
        audit.check(f"{label} parents exact", child["parent_ids"] == EXPECTED_PARENT_IDS, child["parent_ids"], EXPECTED_PARENT_IDS, "children")
        audit.check(f"{label} all pass", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "children")
        audit.check(f"{label} next gate", child["next_gate"] == "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", child["next_gate"], "sideways gate", "children")
    audit.check("independent cross invariants", fresh_primary["cross_invariants"] == fresh_independent["cross_invariants"], fresh_primary["cross_invariants"], fresh_independent["cross_invariants"], "cross")
    audit.check("independent scope", fresh_primary["scope"] == fresh_independent["scope"] == manifest["scope"], [fresh_primary["scope"], fresh_independent["scope"]], manifest["scope"], "cross")
    audit.check("independent negatives", fresh_primary["negative_ids"] == fresh_independent["negative_ids"] == manifest["negative_ids"], [fresh_primary["negative_ids"], fresh_independent["negative_ids"]], manifest["negative_ids"], "cross")
    audit.check("independent scripts differ", sha256(PRIMARY_SCRIPT) != sha256(INDEPENDENT_SCRIPT), [sha256(PRIMARY_SCRIPT), sha256(INDEPENDENT_SCRIPT)], "different", "independence")
    independent_text = INDEPENDENT_SCRIPT.read_text(encoding="utf-8")
    audit.check("independent no SymPy", "import sympy" not in independent_text, "import sympy" in independent_text, False, "independence")
    audit.check("independent no NumPy", "import numpy" not in independent_text.lower() and "from numpy" not in independent_text.lower(), ["import numpy" in independent_text.lower(), "from numpy" in independent_text.lower()], [False, False], "independence")
    audit.check("independent no primary import", "from pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split import" not in independent_text, "primary import" in independent_text, False, "independence")
    audit.check("independent Fraction route", "from fractions import Fraction" in independent_text, "from fractions import Fraction" in independent_text, True, "independence")
    audit.check("independent derives matrices", "def multiply(" in independent_text and "def rank(" in independent_text, ["def multiply(" in independent_text, "def rank(" in independent_text], [True, True], "independence")
    audit.check("independent derives polynomials", "def poly_multiply(" in independent_text and "def poly_power(" in independent_text, ["def poly_multiply(" in independent_text, "def poly_power(" in independent_text], [True, True], "independence")

    audit.check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest parent IDs exact", manifest["parent_ids"] == EXPECTED_PARENT_IDS, manifest["parent_ids"], EXPECTED_PARENT_IDS, "manifest")
    loaded_parent_ids = [load_json(path)["candidate_id"] for path in parent_paths]
    audit.check("loaded parent IDs exact", loaded_parent_ids == EXPECTED_PARENT_IDS, loaded_parent_ids, EXPECTED_PARENT_IDS, "parents")
    authority_hashes = {str(path.relative_to(REPO)).replace("\\", "/"): sha256(path) for path in parent_paths}
    for label, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        expected_child_hashes = {
            "q3lock_manifest": sha256(Q3LOCK),
            "semidiscrete_manifest": sha256(SEMIDISCRETE),
            "strict_cone_manifest": sha256(STRICT_CONE),
            "quantum_state_manifest": sha256(QUANTUM_STATE),
            "boundary_split_manifest": sha256(BOUNDARY_SPLIT),
        }
        for key, expected_hash in expected_child_hashes.items():
            audit.check(f"{label} parent hash: {key}", child["source_sha256"][key] == expected_hash, child["source_sha256"][key], expected_hash, "hashes")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "hashes")

    audit.check("one B(H) algebra declared", manifest["quantum_circuit"]["algebra"].startswith("B(H_a)"), manifest["quantum_circuit"]["algebra"], "B(H_a)", "contracts")
    audit.check("Weyl distinction declared", "kept distinct" in manifest["quantum_circuit"]["algebra"], manifest["quantum_circuit"]["algebra"], "kept distinct", "contracts")
    audit.check("canonical p declared", "p_(j,e)=w*Pi_(j,e)" in manifest["finite_regulator"]["field_variables"], manifest["finite_regulator"]["field_variables"], "p=w Pi", "contracts")
    audit.check("same autonomous comparator", "exactly the inherited" in manifest["finite_regulator"]["autonomous_comparator"], manifest["finite_regulator"]["autonomous_comparator"], "inherited H", "contracts")
    audit.check("state transport not stationarity", "transport is not stationarity" in manifest["state_transport"]["selection_boundary"], manifest["state_transport"]["selection_boundary"], "not stationarity", "contracts")
    audit.check("parent gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "contracts")
    audit.check("four closed subgates", len(manifest["gate_resolution"]["closed_subgates"]) == 4, len(manifest["gate_resolution"]["closed_subgates"]), 4, "contracts")
    audit.check("four refuted subgates", len(manifest["gate_resolution"]["refuted_subgates"]) == 4, len(manifest["gate_resolution"]["refuted_subgates"]), 4, "contracts")
    audit.check("next gate exact", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT", "contracts")

    certificate_phrases = (
        "causal Cauchy Floquet circuit",
        "J_D^T J J_D = J",
        "partial F_delta^n(z)_j / partial z_k = 0",
        "normal unital star automorphism",
        "det S_delta(k) = 1",
        "Tr(rho_n A) = Tr(rho alpha_delta^n(A))",
        "not uniformly continuous",
        "1 + (delta omega)^4/4",
        "Tr exp(-beta H_F,principal) = infinity",
        "outer product has rank one, not two",
        "The next route is",
        "C0, N1-N5, CP1, and Pre-A",
    )
    for phrase in certificate_phrases:
        audit.check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")
    for section in range(1, 15):
        audit.check(f"certificate section {section}", f"## {section}." in certificate_text, f"## {section}." in certificate_text, True, "certificate")

    negative_ids = manifest["negative_ids"]
    for negative_id in negative_ids:
        anchor = negative_id.lower()
        audit.check(f"negative summary: {negative_id}", f"[{negative_id}]" in registry_text, f"[{negative_id}]" in registry_text, True, "records")
        audit.check(f"negative section: {negative_id}", f"### {negative_id}" in registry_text, f"### {negative_id}" in registry_text, True, "records")
        audit.check(f"negative anchor: {negative_id}", f'id="{anchor}"' in registry_text, f'id="{anchor}"' in registry_text, True, "records")

    manifest_ref = f"strategy/{SLUG}-manifest.json"
    matching_explorations = [
        record
        for record in exploration_records
        if manifest_ref in record.get("evidence_refs", [])
        or any(reference.startswith(manifest_ref + "#") for reference in record.get("evidence_refs", []))
    ]
    audit.check("one exploration route record", len(matching_explorations) == 1, [record.get("id") for record in matching_explorations], "one", "records")
    route_record = matching_explorations[0]
    audit.check("exploration task", route_record["task_id"] == "T-054", route_record["task_id"], "T-054", "records")
    audit.check("exploration verdict", route_record["verdict"] == "advanced", route_record["verdict"], "advanced", "records")
    audit.check("exploration negatives", route_record["formal_refs"]["negatives"] == negative_ids, route_record["formal_refs"]["negatives"], negative_ids, "records")
    audit.check("exploration no formal results", route_record["formal_refs"]["results"] == [], route_record["formal_refs"]["results"], [], "records")
    index_manifest_name = f"{SLUG}-manifest.json"
    audit.check("strategy index row", index_manifest_name in index_text, index_manifest_name in index_text, True, "records")
    task = next(item for item in todo_data["tasks"] if item["id"] == "T-054")
    audit.check("TODO next gate", "PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT" in task["note"], "sideways gate" in task["note"], True, "records")
    audit.check("TODO exploration id", route_record["id"] in task["note"], route_record["id"] in task["note"], True, "records")
    matching_events = [record for record in changelog_records if manifest_ref in record.get("notes", [])]
    audit.check("one changelog event", len(matching_events) == 1, [record.get("id") for record in matching_events], "one", "records")
    audit.check("changelog negatives", sorted(matching_events[0]["neg_results"]) == sorted(negative_ids), matching_events[0]["neg_results"], sorted(negative_ids), "records")

    audit.check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    audit.check("C6 tier unchanged", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    audit.check("C6 lifecycle unchanged", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    audit.check("C6 evidence unchanged", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    audit.check("C6 gate unchanged", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    true_keys = (
        "fixed_regulator_exact_symplectic_Cauchy_circuit",
        "fixed_regulator_exact_reversibility",
        "fixed_regulator_exact_radius_one_cone",
        "full_interacting_BH_quantum_automorphism",
        "exact_density_state_transport",
        "quadratic_metaplectic_Weyl_covariance",
        "exact_Floquet_symbol_and_CFL",
    )
    for key in true_keys:
        audit.check(f"integrated scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    false_keys = (
        "full_nonlinear_Weyl_Cstar_invariance",
        "inherited_autonomous_H_conserved",
        "inherited_ground_or_Gibbs_stationary",
        "principal_Floquet_log_trace_class_Gibbs",
        "two_null_side_characteristic_reconstruction",
        "locally_sideways_invertible",
        "common_characteristic_model_gate_closed",
        "preferred_physical_state_selected",
        "physical_energy_reference",
        "physical_vacuum",
        "below_empty_space",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
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
    for key in false_keys:
        audit.check(f"integrated scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    forbidden_claims = (
        "Pre-A is proved",
        "Pre-A is complete",
        "physical vacuum is selected",
        "below empty space is proved",
        "event horizon is derived",
        "C6 is advanced",
    )
    public_text = manifest["statement"] + "\n" + manifest["no_overclaim"] + "\n" + certificate_text
    for phrase in forbidden_claims:
        audit.check(f"no overclaim: {phrase}", phrase not in public_text, phrase in public_text, False, "no_overclaim")

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
        "cross_invariants": fresh_primary["cross_invariants"],
        "derived": fresh_primary["derived"],
        "scope": manifest["scope"],
        "negative_ids": negative_ids,
        "exploration_id": route_record["id"],
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
