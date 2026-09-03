#!/usr/bin/env python3
"""Integrated verifier for the CL8 passive two-arm characteristic control."""

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
CANDIDATE_ID = "PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-PASSIVE-TWO-ARM-CUT-RECONSTRUCTION-AND-CL8-KICK-STATE-NOGO"
SLUG = "pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT_SCRIPT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
COMMON_PARENT = REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json"
GOURSAT_PARENT = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
BOUNDARY_PARENT = REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json"
GAUSSIAN_PARENT = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
Q3_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
PARENT_PRIMARY_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-04-primary-pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split/result.json"
)
PARENT_INDEPENDENT_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-04-independent-pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split/result.json"
)
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
TODO_JSON = REPO / "todo/todo.json"
CHANGELOG_JSONL = REPO / "changelog/log.jsonl"
CATALOG_MD = REPO / "CATALOG.md"
CATALOG_JSON = REPO / "verification/catalog.json"
PROOF_MAP_MD = REPO / "theory/proof-evidence-map.md"
PROOF_MAP_JSON = REPO / "verification/proof-evidence-map.json"
LINEAGE = REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md"
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
EXPECTED_PRIMARY_ASSERTIONS = 117
EXPECTED_INDEPENDENT_ASSERTIONS = 114
EXPECTED_PARENT_IDS = [
    "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
    "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
    "PA-CP1-ST8-Q3LOCK-v0",
]
EXPECTED_NEGATIVE = "NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE"
NEXT_GATE = "PA-CP1-CL8-INTERACTING-GATE-TILING-ALL-CUT-INVARIANT-OR-WORK-STATE"


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


def run_child(script: Path, output: Path, extra: list[str] | None = None) -> dict[str, Any]:
    command = [sys.executable, str(script), "--output", str(output)]
    if extra:
        command.extend(extra)
    completed = subprocess.run(
        command,
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script.name}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return load_json(output)


def float_paths(value: Any, prefix: str = "root") -> list[str]:
    found: list[str] = []
    if isinstance(value, float):
        found.append(prefix)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(float_paths(item, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(float_paths(item, f"{prefix}[{index}]"))
    return found


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
    parent_paths = (COMMON_PARENT, GOURSAT_PARENT, BOUNDARY_PARENT, GAUSSIAN_PARENT, Q3_PARENT)
    required_files = (
        PRIMARY_SCRIPT,
        INDEPENDENT_SCRIPT,
        MANIFEST,
        CERTIFICATE,
        *parent_paths,
        PARENT_PRIMARY_RESULT,
        PARENT_INDEPENDENT_RESULT,
        C6_STATUS,
        NEGATIVE_REGISTRY,
        EXPLORATIONS,
        STRATEGY_INDEX,
        TODO_JSON,
        CHANGELOG_JSONL,
        CATALOG_MD,
        CATALOG_JSON,
        PROOF_MAP_MD,
        PROOF_MAP_JSON,
        LINEAGE,
        PRIMARY_RESULT,
        INDEPENDENT_RESULT,
    )
    for path in required_files:
        audit.check(f"required file: {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = load_json(MANIFEST)
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    c6_status = load_json(C6_STATUS)
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    exploration_records = [
        json.loads(line)
        for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    todo_data = load_json(TODO_JSON)
    changelog_records = [
        json.loads(line)
        for line in CHANGELOG_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    with tempfile.TemporaryDirectory(prefix="tect-cl8-passive-two-arm-") as directory:
        temporary = Path(directory)
        fresh_primary = run_child(PRIMARY_SCRIPT, temporary / "primary.json")
        fresh_independent = run_child(INDEPENDENT_SCRIPT, temporary / "independent.json")
        mutated_primary = run_child(
            PRIMARY_SCRIPT,
            temporary / "primary-mutated.json",
            [
                "--pythagorean-u",
                "4",
                "--pythagorean-v",
                "1",
                "--rectangle-m",
                "3",
                "--rectangle-n",
                "7",
                "--ring-size",
                "10",
                "--fugacity-numerator",
                "3",
                "--fugacity-denominator",
                "8",
            ],
        )
        mutated_independent = run_child(
            INDEPENDENT_SCRIPT,
            temporary / "independent-mutated.json",
            [
                "--pythagorean-u",
                "4",
                "--pythagorean-v",
                "3",
                "--rectangle-m",
                "4",
                "--rectangle-n",
                "6",
                "--ring-size",
                "10",
                "--fugacity-numerator",
                "4",
                "--fugacity-denominator",
                "9",
            ],
        )
        shared_arguments = [
            "--pythagorean-u",
            "5",
            "--pythagorean-v",
            "2",
            "--rectangle-m",
            "2",
            "--rectangle-n",
            "8",
            "--ring-size",
            "10",
            "--fugacity-numerator",
            "3",
            "--fugacity-denominator",
            "8",
        ]
        shared_primary = run_child(PRIMARY_SCRIPT, temporary / "primary-shared.json", shared_arguments)
        shared_independent = run_child(INDEPENDENT_SCRIPT, temporary / "independent-shared.json", shared_arguments)
    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    audit.check("stored primary equals fresh", stored_primary == fresh_primary, sha256(PRIMARY_RESULT), "fresh payload", "freshness")
    audit.check("stored independent equals fresh", stored_independent == fresh_independent, sha256(INDEPENDENT_RESULT), "fresh payload", "freshness")
    audit.check("primary count", fresh_primary["assertion_summary"] == {"passed": EXPECTED_PRIMARY_ASSERTIONS, "total": EXPECTED_PRIMARY_ASSERTIONS}, fresh_primary["assertion_summary"], EXPECTED_PRIMARY_ASSERTIONS, "children")
    audit.check("independent count", fresh_independent["assertion_summary"] == {"passed": EXPECTED_INDEPENDENT_ASSERTIONS, "total": EXPECTED_INDEPENDENT_ASSERTIONS}, fresh_independent["assertion_summary"], EXPECTED_INDEPENDENT_ASSERTIONS, "children")
    for label, child in (("primary", fresh_primary), ("independent", fresh_independent)):
        audit.check(f"{label} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "children")
        audit.check(f"{label} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "children")
        audit.check(f"{label} parents", child["parent_ids"] == EXPECTED_PARENT_IDS, child["parent_ids"], EXPECTED_PARENT_IDS, "children")
        audit.check(f"{label} claim nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "children")
        audit.check(f"{label} next gate", child["next_gate"] == NEXT_GATE, child["next_gate"], NEXT_GATE, "children")
        audit.check(f"{label} all pass", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "children")
        audit.check(f"{label} no floats", float_paths(child) == [], float_paths(child), [], "independence")
    audit.check("cross invariants agree", fresh_primary["cross_invariants"] == fresh_independent["cross_invariants"], fresh_primary["cross_invariants"], fresh_independent["cross_invariants"], "cross")
    audit.check("scope agrees", fresh_primary["scope"] == fresh_independent["scope"] == manifest["scope"], [fresh_primary["scope"], fresh_independent["scope"]], manifest["scope"], "cross")
    audit.check("negative agrees", fresh_primary["negative_ids"] == fresh_independent["negative_ids"] == manifest["negative_ids"], [fresh_primary["negative_ids"], fresh_independent["negative_ids"]], manifest["negative_ids"], "cross")
    audit.check("fixture gamma differs", fresh_primary["derived"]["gamma"] != fresh_independent["derived"]["gamma"], [fresh_primary["derived"]["gamma"], fresh_independent["derived"]["gamma"]], "different", "cross")
    audit.check("fixture geometry differs", fresh_primary["derived"]["rectangle"] != fresh_independent["derived"]["rectangle"], [fresh_primary["derived"]["rectangle"], fresh_independent["derived"]["rectangle"]], "different", "cross")

    audit.check("primary mutation changes gamma", mutated_primary["derived"]["gamma"] != fresh_primary["derived"]["gamma"], [mutated_primary["derived"]["gamma"], fresh_primary["derived"]["gamma"]], "changed", "mutation")
    audit.check("primary mutation changes cut count", mutated_primary["derived"]["cut_count"] != fresh_primary["derived"]["cut_count"], [mutated_primary["derived"]["cut_count"], fresh_primary["derived"]["cut_count"]], "changed", "mutation")
    audit.check("primary mutation changes brickwork", mutated_primary["derived"]["brickwork"] != fresh_primary["derived"]["brickwork"], "changed", "changed", "mutation")
    audit.check("primary mutation keeps invariants", mutated_primary["cross_invariants"] == fresh_primary["cross_invariants"], mutated_primary["cross_invariants"], fresh_primary["cross_invariants"], "mutation")
    audit.check("independent mutation changes gamma", mutated_independent["derived"]["gamma"] != fresh_independent["derived"]["gamma"], [mutated_independent["derived"]["gamma"], fresh_independent["derived"]["gamma"]], "changed", "mutation")
    audit.check("independent mutation changes cut count", mutated_independent["derived"]["cut_count"] != fresh_independent["derived"]["cut_count"], [mutated_independent["derived"]["cut_count"], fresh_independent["derived"]["cut_count"]], "changed", "mutation")
    audit.check("independent mutation changes brickwork", mutated_independent["derived"]["brickwork"] != fresh_independent["derived"]["brickwork"], "changed", "changed", "mutation")
    audit.check("independent mutation keeps invariants", mutated_independent["cross_invariants"] == fresh_independent["cross_invariants"], mutated_independent["cross_invariants"], fresh_independent["cross_invariants"], "mutation")
    shared_fields = (
        "gamma",
        "eta",
        "local_gate",
        "eta_sideways",
        "gamma_sideways",
        "boundary_transfer",
        "cut_count",
        "cut_fingerprints",
        "brickwork",
        "causal_violations",
        "one_period_radius_violations",
        "inverse_radius_violations",
        "two_period_radius_violations",
        "fugacity",
        "mode_count",
        "Gibbs_partition",
        "rectangle",
        "ring_size",
    )
    for key in shared_fields:
        audit.check(
            f"shared-fixture agreement: {key}",
            shared_primary["derived"][key] == shared_independent["derived"][key],
            shared_primary["derived"][key],
            shared_independent["derived"][key],
            "cross",
        )

    primary_text = PRIMARY_SCRIPT.read_text(encoding="utf-8")
    independent_text = INDEPENDENT_SCRIPT.read_text(encoding="utf-8")
    audit.check("scripts differ", sha256(PRIMARY_SCRIPT) != sha256(INDEPENDENT_SCRIPT), [sha256(PRIMARY_SCRIPT), sha256(INDEPENDENT_SCRIPT)], "different", "independence")
    audit.check("independent no SymPy", "sympy" not in independent_text.lower(), "sympy" in independent_text.lower(), False, "independence")
    audit.check("independent no NumPy", "numpy" not in independent_text.lower(), "numpy" in independent_text.lower(), False, "independence")
    audit.check("independent no primary import", PRIMARY_SCRIPT.stem not in independent_text, PRIMARY_SCRIPT.stem in independent_text, False, "independence")
    audit.check("independent Fraction", "from fractions import Fraction" in independent_text, "from fractions import Fraction" in independent_text, True, "independence")
    audit.check("independent matrix implementation", "def multiply(" in independent_text and "def rank(" in independent_text, ["def multiply(" in independent_text, "def rank(" in independent_text], [True, True], "independence")
    pasted_literals = ("Rational(3, 5)", "Rational(4, 5)", "Fraction(3, 5)", "Fraction(4, 5)", "Fraction(5, 13)", "Fraction(12, 13)")
    audit.check("primary no pasted derived fixture", not any(item in primary_text for item in pasted_literals), [item for item in pasted_literals if item in primary_text], [], "hardcode")
    audit.check("independent no pasted derived fixture", not any(item in independent_text for item in pasted_literals), [item for item in pasted_literals if item in independent_text], [], "hardcode")

    audit.check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest parents", manifest["parent_ids"] == EXPECTED_PARENT_IDS, manifest["parent_ids"], EXPECTED_PARENT_IDS, "manifest")
    audit.check("manifest negative", manifest["negative_ids"] == [EXPECTED_NEGATIVE], manifest["negative_ids"], [EXPECTED_NEGATIVE], "manifest")
    audit.check("manifest T0", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "manifest")
    audit.check("passive split status", manifest["gate_resolution"]["status"] == "PASSIVE LINEAR-CONTROL SUBGATE CLOSED; INTERACTING PARENT REMAINS OPEN", manifest["gate_resolution"]["status"], "passive only", "manifest")
    audit.check("next gate exact", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "manifest")
    loaded_parent_ids = [load_json(path)["candidate_id"] for path in parent_paths]
    audit.check("loaded parent IDs", loaded_parent_ids == EXPECTED_PARENT_IDS, loaded_parent_ids, EXPECTED_PARENT_IDS, "parents")
    expected_hash_keys = {
        "common_parent": COMMON_PARENT,
        "goursat_parent": GOURSAT_PARENT,
        "boundary_parent": BOUNDARY_PARENT,
        "gaussian_parent": GAUSSIAN_PARENT,
        "q3_parent": Q3_PARENT,
    }
    for label, child, parent_result in (
        ("primary", fresh_primary, PARENT_PRIMARY_RESULT),
        ("independent", fresh_independent, PARENT_INDEPENDENT_RESULT),
    ):
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "hashes")
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(PRIMARY_SCRIPT if label == "primary" else INDEPENDENT_SCRIPT), child["source_sha256"]["script"], "current", "hashes")
        audit.check(f"{label} parent-result hash", child["source_sha256"]["parent_result"] == sha256(parent_result), child["source_sha256"]["parent_result"], sha256(parent_result), "hashes")
        for key, path in expected_hash_keys.items():
            audit.check(f"{label} authority hash: {key}", child["source_sha256"][key] == sha256(path), child["source_sha256"][key], sha256(path), "hashes")

    for section in range(1, 14):
        audit.check(f"certificate section {section}", f"## {section}." in certificate_text, f"## {section}." in certificate_text, True, "certificate")
    anchors = (
        "section-3-passive-local-gate",
        "section-4-oriented-sideways-inverses",
        "section-5-two-arm-boundary-and-corner",
        "section-6-all-cut-reconstruction",
        "section-8-quantum-cut-map",
        "section-9-positive-generator-and-state",
        "section-10-cl8-quartic-reuse-no-go",
    )
    for anchor in anchors:
        audit.check(f"certificate anchor: {anchor}", f'id="{anchor}"' in certificate_text, f'id="{anchor}"' in certificate_text, True, "certificate")
    phrases = (
        "rank-eight D-K-D neighbour block",
        "There is no duplicated corner coordinate",
        "binomial(m+n,m)",
        "C_I^T C_I=I",
        "alpha(W(z))=W(C_I^(-1)z)",
        "Tr zeta^N=(1-zeta)^(-D)",
        "<4|[N,Q^4]|0>",
        "dual-unitarity: the literal four-leg kernel",
        "`C0`, `N1`--`N5`, `C6`, `CP1`, and `Pre-A`",
    )
    for phrase in phrases:
        audit.check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")

    negative_anchor = EXPECTED_NEGATIVE.lower()
    audit.check("negative summary", f"[{EXPECTED_NEGATIVE}]" in registry_text, f"[{EXPECTED_NEGATIVE}]" in registry_text, True, "records")
    audit.check("negative section", f"### {EXPECTED_NEGATIVE}" in registry_text, f"### {EXPECTED_NEGATIVE}" in registry_text, True, "records")
    audit.check("negative anchor", f'id="{negative_anchor}"' in registry_text, f'id="{negative_anchor}"' in registry_text, True, "records")

    manifest_ref = f"strategy/{SLUG}-manifest.json"
    matching_explorations = [
        record
        for record in exploration_records
        if manifest_ref in record.get("evidence_refs", [])
        or any(reference.startswith(manifest_ref + "#") for reference in record.get("evidence_refs", []))
    ]
    audit.check("one exploration", len(matching_explorations) == 1, [record.get("id") for record in matching_explorations], "one", "records")
    route_record = matching_explorations[0]
    audit.check("exploration task", route_record["task_id"] == "T-054", route_record["task_id"], "T-054", "records")
    audit.check("exploration verdict", route_record["verdict"] == "advanced", route_record["verdict"], "advanced", "records")
    audit.check("exploration negative", route_record["formal_refs"]["negatives"] == [EXPECTED_NEGATIVE], route_record["formal_refs"]["negatives"], [EXPECTED_NEGATIVE], "records")
    audit.check("exploration no results", route_record["formal_refs"]["results"] == [], route_record["formal_refs"]["results"], [], "records")
    audit.check("strategy index", f"{SLUG}-manifest.json" in index_text, f"{SLUG}-manifest.json" in index_text, True, "records")
    task = next(item for item in todo_data["tasks"] if item["id"] == "T-054")
    audit.check("TODO exploration", route_record["id"] in task["note"], route_record["id"] in task["note"], True, "records")
    audit.check("TODO next gate", NEXT_GATE in task["note"], NEXT_GATE in task["note"], True, "records")
    events = [record for record in changelog_records if manifest_ref in record.get("notes", [])]
    audit.check("one changelog event", len(events) == 1, [record.get("id") for record in events], "one", "records")
    audit.check("changelog negative", events[0]["neg_results"] == [EXPECTED_NEGATIVE], events[0]["neg_results"], [EXPECTED_NEGATIVE], "records")

    audit.check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    audit.check("C6 tier", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    audit.check("C6 lifecycle", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    audit.check("C6 evidence", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    audit.check("C6 gate", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    true_scope = (
        "same_CL8_finite_phase_dimension",
        "general_parameter_full_rank_sideways_gate",
        "two_arm_corner_and_dimension_declared",
        "all_admissible_cut_reconstruction",
        "global_sweep_independence",
        "exact_cut_symplecticity",
        "exact_cut_causality",
        "exact_metaplectic_Weyl_cut_maps",
        "exact_BH_cut_isomorphisms",
        "positive_invariant_passive_generator",
        "actual_cut_covariant_normal_Gibbs_state_family",
        "periodic_companion_stationary_normal_Gibbs_state",
        "linear_passive_control_subgate_closed",
        "local_q_only_kicked_gate_classically_sideways_invertible",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    false_scope = (
        "strict_continuous_variable_dual_unitarity",
        "arbitrary_periodic_two_arm_seam_reconstruction",
        "inherited_Q3_interaction_implemented",
        "interacting_CL8_characteristic_parent_closed",
        "passive_number_survives_CL8_quartic_kick",
        "interacting_boundary_bulk_intertwiner",
        "preferred_physical_state_selected",
        "physical_energy_reference",
        "physical_vacuum",
        "below_empty_space",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "speed_of_light_derived",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "full_3_plus_1_dependence",
        "gravity_or_event_horizon",
        "phase_transition_or_cooling",
        "cyclic_cosmology",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    catalog_text = CATALOG_MD.read_text(encoding="utf-8") + CATALOG_JSON.read_text(encoding="utf-8")
    proof_text = PROOF_MAP_MD.read_text(encoding="utf-8") + PROOF_MAP_JSON.read_text(encoding="utf-8")
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    public_paths = (
        f"strategy/{SLUG}-manifest.json",
        f"strategy/{SLUG}-certificate-260804.md",
        f"codes/foundations/{SLUG.replace('-', '_')}.py",
        f"codes/foundations/{SLUG.replace('-', '_')}_independent.py",
        f"codes/foundations/{SLUG.replace('-', '_')}_verify.py",
        f"2026-08-04-primary-{SLUG}",
        f"2026-08-04-independent-{SLUG}",
    )
    for item in public_paths:
        audit.check(f"catalog surface: {item}", item in catalog_text, item in catalog_text, True, "generated")
    audit.check("proof map candidate", CANDIDATE_ID in proof_text, CANDIDATE_ID in proof_text, True, "generated")
    audit.check("proof map exploration", route_record["id"] in proof_text, route_record["id"] in proof_text, True, "generated")
    audit.check("proof map negative", EXPECTED_NEGATIVE in proof_text, EXPECTED_NEGATIVE in proof_text, True, "generated")
    audit.check("lineage primary", f"2026-08-04-primary-{SLUG}" in lineage_text, f"2026-08-04-primary-{SLUG}" in lineage_text, True, "generated")
    audit.check("lineage independent", f"2026-08-04-independent-{SLUG}" in lineage_text, f"2026-08-04-independent-{SLUG}" in lineage_text, True, "generated")

    forbidden = (
        "Pre-A is complete",
        "physical vacuum is selected",
        "below empty space is proved",
        "strict continuous-variable dual-unitary gate is proved",
        "interacting CL8 characteristic parent is closed",
        "speed of light is derived",
    )
    public_text = manifest["statement"] + "\n" + manifest["no_overclaim"] + "\n" + certificate_text
    for phrase in forbidden:
        audit.check(f"no overclaim: {phrase}", phrase not in public_text, phrase in public_text, False, "no_overclaim")

    authority_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): sha256(path)
        for path in parent_paths
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": EXPECTED_PARENT_IDS,
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
        "mutation": {
            "primary_gamma": mutated_primary["derived"]["gamma"],
            "primary_cut_count": mutated_primary["derived"]["cut_count"],
            "independent_gamma": mutated_independent["derived"]["gamma"],
            "independent_cut_count": mutated_independent["derived"]["cut_count"],
        },
        "cross_invariants": fresh_primary["cross_invariants"],
        "derived": fresh_primary["derived"],
        "scope": manifest["scope"],
        "negative_ids": [EXPECTED_NEGATIVE],
        "exploration_id": route_record["id"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": NEXT_GATE,
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary_script": sha256(PRIMARY_SCRIPT),
            "independent_script": sha256(INDEPENDENT_SCRIPT),
            "negative_registry": sha256(NEGATIVE_REGISTRY),
            "explorations": sha256(EXPLORATIONS),
            "strategy_index": sha256(STRATEGY_INDEX),
            "todo_json": sha256(TODO_JSON),
            "changelog_jsonl": sha256(CHANGELOG_JSONL),
            "c6_status": sha256(C6_STATUS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} integrated: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
