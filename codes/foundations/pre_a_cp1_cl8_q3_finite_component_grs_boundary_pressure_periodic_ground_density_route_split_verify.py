#!/usr/bin/env python3
"""Integrated verifier for the finite-component GRS Q3 density theorem."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-HALF-PERIODIC-PRESSURE-PERIODIC-GROUND-AND-SPECIFIC-KL-DENSITY"
EXPLORATION_ID = "EXP-000778"
PARENT_EXPLORATION = "EXP-000777"
SURFACE_GATE = "PA-CP1-CL8-Q3-CUTOFF-VOLUME-INTERPOLATION-UNIFORM-PERIODIC-SHARP-SURFACE-PAIRING"
NEXT_GATE = "PA-CP1-CL8-Q3-PHASE-PHYSICAL-REFERENCE-AND-ONE-DIMENSIONAL-TO-THREE-DIMENSIONAL-PARENT-ROUTE-SPLIT"
PARENT_CANDIDATE_ID = "PA-CP1-CL8-Q3-ZERO-TEMPERATURE-THERMODYNAMIC-GROUND-PHASE-AND-PHYSICAL-REFERENCE-ROUTE-SPLIT-v0"
REUSED_NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-FINITE-CIRCLE-WITNESS-ZERO-TEMPERATURE-DENSITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-VOLUME-UI-PERIODIC-SHARP-SURFACE-PAIRING",
    "NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR",
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT",
]
CLOSED_SUBGATES = [
    "PA-CP1-CL8-Q3-GRS-UNIFORM-SUBDOMINANT-COUPLING",
    "PA-CP1-CL8-Q3-ALL-SIXTEEN-FULL-HALF-BOUNDARY-PRESSURE-DENSITY",
    "PA-CP1-CL8-Q3-HALF-PERIODIC-GROUND-ENERGY-DENSITY",
    "PA-CP1-CL8-Q3-PERIODIC-ZERO-TEMPERATURE-SPECIFIC-KL-DENSITY",
    "PA-CP1-CL8-Q3-SCALAR-BETA-L-VAN-HOVE-LIMIT-INTERCHANGE",
]
OPEN_SUBGATES = [
    "PA-CP1-CL8-Q3-PHASE-ORDER-PARAMETER-AND-BOUNDARY-STATE-CLASSIFICATION",
    "PA-CP1-CL8-Q3-PHYSICAL-EMPTY-SPACE-AND-STRESS-TENSOR-RENORMALIZATION-ANCHOR",
    "PA-CP1-CL8-Q3-ZERO-TEMPERATURE-STATE-GROUND-VECTOR-GAP-AND-CORRELATION-LIMITS",
    "PA-CP1-CL8-INTERACTING-MICROLOCAL-SPECTRUM-OR-RELATIVISTIC-KMS",
    "PA-CP1-CL8-ONE-DIMENSIONAL-TO-THREE-DIMENSIONAL-Q3-PARENT",
    "PA-PRE-A-C0-N1-N5-VALIDATION",
]
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
PARENT_STORED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


def sha256(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def canonical(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], tuple[int, int]]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", completed.stdout.strip())
    if match is None:
        raise AssertionError(completed.stdout)
    return json.loads(output.read_text(encoding="utf-8")), (int(match.group(1)), int(match.group(2)))


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    result |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    return result


def exploration_record() -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == EXPLORATION_ID:
            return record
    raise AssertionError(f"missing {EXPLORATION_ID}")


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("no new negative", manifest["negative_ids"] == [], manifest["negative_ids"], [], "identity")
    audit.check("exact reused negatives", manifest["reused_negative_ids"] == REUSED_NEGATIVE_IDS, manifest["reused_negative_ids"], REUSED_NEGATIVE_IDS, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == SURFACE_GATE, manifest["gate_resolution"]["parent_gate"], SURFACE_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("closed subgates", manifest["gate_resolution"]["closed_subgates"] == CLOSED_SUBGATES, manifest["gate_resolution"]["closed_subgates"], CLOSED_SUBGATES, "identity")
    audit.check("non-load-bearing gate", manifest["gate_resolution"]["non_load_bearing_open_subgates"] == [SURFACE_GATE], manifest["gate_resolution"]["non_load_bearing_open_subgates"], [SURFACE_GATE], "identity")
    audit.check("open subgates", manifest["gate_resolution"]["open_subgates"] == OPEN_SUBGATES, manifest["gate_resolution"]["open_subgates"], OPEN_SUBGATES, "identity")
    parent = json.loads(PARENT_STORED.read_text(encoding="utf-8"))
    audit.check("parent identity", parent["candidate_id"] == PARENT_CANDIDATE_ID and parent["exploration_id"] == PARENT_EXPLORATION, (parent["candidate_id"], parent["exploration_id"]), (PARENT_CANDIDATE_ID, PARENT_EXPLORATION), "parent")
    audit.check("parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    with tempfile.TemporaryDirectory(prefix="tect-q3-grs-boundary-density-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(f"{label} identity", child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID, (child["candidate_id"], child["result_id"]), (CANDIDATE_ID, RESULT_ID), "children")
        audit.check(f"{label} no new negative", child["negative_ids"] == [], child["negative_ids"], [], "children")
        audit.check(f"{label} scope", child["scope"] == manifest["scope"], child["scope"], manifest["scope"], "children")
        audit.check(f"{label} next gate", child["next_gate"] == NEXT_GATE, child["next_gate"], NEXT_GATE, "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical(primary_stored) == canonical(primary), sha256(PRIMARY_STORED), "fresh", "stored")
    audit.check("stored independent fresh", canonical(independent_stored) == canonical(independent), sha256(INDEPENDENT_STORED), "fresh", "stored")
    for label, child, source in (("primary", primary, PRIMARY), ("independent", independent, INDEPENDENT)):
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(source), child["source_sha256"]["script"], sha256(source), "stored")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "stored")
        audit.check(f"{label} certificate hash", child["source_sha256"]["certificate"] == sha256(CERTIFICATE), child["source_sha256"]["certificate"], sha256(CERTIFICATE), "stored")
        audit.check(f"{label} parent hash", child["source_sha256"]["parent"] == sha256(PARENT_STORED), child["source_sha256"]["parent"], sha256(PARENT_STORED), "stored")

    independent_imports = imports(INDEPENDENT)
    audit.check("independent no primary import", PRIMARY.stem not in independent_imports, sorted(independent_imports), f"not {PRIMARY.stem}", "independence")
    audit.check("independent stdlib only", not ({"sympy", "mpmath", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "stdlib only", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    primary_names = {row["name"] for row in primary["assertions"]}
    independent_names = {row["name"] for row in independent["assertions"]}
    for name in (
        "Q3 Wick Laplacian matrix identity",
        "exact boundary Wick reordering identity",
        "multivariate Wick conditioning identity",
        "tensor covariance order fixture",
        "quadratic Young identity is a square",
        "boundary Wick coupling norm vanishes",
        "convex bounded-ball Lipschitz fixture",
        "all sixteen full-half boundary pairs",
        "half-periodic convention distinct",
        "Section VIII Wick pair classification",
        "reused P-F notation has distinct semantics",
        "sequence diagonal projection error vanishes",
        "sequence diagonal ground density converges",
        "specific KL tends alpha fixture",
        "raw ground sign scalar mutable",
        "rectangle KL exchange symmetry",
        "joint scalar KL density converges",
        "stronger surface gate retained",
    ):
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in (
        "independent multivariate Wick conditioning",
        "independent Q3 Wick Laplacian",
        "independent exact boundary Wick reordering",
        "independent tensor covariance order",
        "independent quadratic Young absorption",
        "independent boundary coupling norm tends zero",
        "independent convex Lipschitz fixture",
        "independent all sixteen boundary pairs",
        "independent half versus full periodic",
        "independent Section VIII pair counts",
        "independent reused P-F notation separation",
        "independent diagonal transfer error",
        "independent ground density convergence",
        "independent specific KL limit fixture",
        "independent KL exchange symmetry",
        "independent joint KL convergence",
    ):
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    audit.check("cross Q3 graph", len(primary["derived"]["Q3"]["edges"]) == independent["derived"]["Q3"]["edges"] == 12, (len(primary["derived"]["Q3"]["edges"]), independent["derived"]["Q3"]["edges"]), 12, "cross")
    audit.check("cross sixteen pairs", len(primary["derived"]["boundary"]["pairs"]) == len(independent["derived"]["boundary"]["pairs"]) == 16, (len(primary["derived"]["boundary"]["pairs"]), len(independent["derived"]["boundary"]["pairs"])), 16, "cross")
    audit.check("cross dual notation separation", primary["derived"]["boundary"]["wick_semantics"]["P;F"] == "half-X" and primary["derived"]["boundary"]["direction_semantics"]["P|F"] == "coordinate-mixed-full" and independent["derived"]["boundary"]["wick_tags"]["P;F"] == "non-diagonal-half-X" and independent["derived"]["boundary"]["direction_tags"]["P|F"] == "coordinate-mixed-full", "Section VIII Half-P versus Section VI mixed-full", "distinct", "cross")
    audit.check("cross boundary decay", primary["derived"]["boundary"]["rows"][-1]["coupling_norm"] < primary["derived"]["boundary"]["rows"][0]["coupling_norm"] and independent["derived"]["boundary"]["rows"][-1]["total"] < independent["derived"]["boundary"]["rows"][0]["total"], "both decrease", "both decrease", "cross")
    audit.check("cross transfer convergence", primary["derived"]["transfer"][-1]["projection_error"] < primary["derived"]["transfer"][0]["projection_error"] and independent["derived"]["transfer"][-1]["error"] < independent["derived"]["transfer"][0]["error"], "both decrease", "both decrease", "cross")
    primary_alpha = primary["derived"]["ledger"]["target_alpha"]
    independent_alpha = independent["derived"]["ledger"]["target_alpha"]
    audit.check("cross KL convergence", abs(primary["derived"]["ledger"]["rectangles"][-1]["d"] - primary_alpha) < abs(primary["derived"]["ledger"]["rectangles"][0]["d"] - primary_alpha) and abs(independent["derived"]["ledger"]["rectangles"][-1]["density"] - independent_alpha) < abs(independent["derived"]["ledger"]["rectangles"][0]["density"] - independent_alpha), (primary["derived"]["ledger"]["rectangles"], independent["derived"]["ledger"]["rectangles"]), "errors decrease to targets", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "Vector Gaussian conditioning and multivariate Wick identity",
        "Uniform subdominant-coupling theorem",
        "two-sided bound",
        "all sixteen",
        "Half-periodic transfer and the diagonal argument",
        "must not be confused with the Section VI mixed-strip notation",
        "Theorem VI.7",
        "choice `t_n>=n`",
        "What the old surface gate now means",
        "physical empty space",
        "It proves no phase transition",
        "derived three-dimensional Q3LOCK",
        "Pre-A",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index", MANIFEST.name in index and CERTIFICATE.name in index, (MANIFEST.name, CERTIFICATE.name), "indexed", "records")
    exploration = exploration_record()
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration no result card", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "claim nonbearing", "records")
    audit.check("exploration parent", any(item.get("id") == PARENT_EXPLORATION for item in exploration.get("related", [])), exploration.get("related"), PARENT_EXPLORATION, "records")
    audit.check("exploration continues both parents", {(item.get("id"), item.get("relation")) for item in exploration.get("related", [])} == {(PARENT_EXPLORATION, "continues"), ("EXP-000775", "continues")}, exploration.get("related"), "EXP770 and EXP768 continue", "records")
    audit.check("exploration next gate", NEXT_GATE in exploration["next_action"], exploration["next_action"], NEXT_GATE, "records")
    todo_payload = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    task = next(item for item in todo_payload["tasks"] if item["id"] == "T-054")
    audit.check("TODO record", task["status"] == "in_progress" and EXPLORATION_ID in task["note"] and NEXT_GATE in task["note"], task, "active route history", "records")
    changelog_records = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()]
    changelog = next(item for item in changelog_records if EXPLORATION_ID in item.get("header", ""))
    audit.check("changelog record", MANIFEST.relative_to(REPO).as_posix() in changelog["notes"] and SCRIPT.relative_to(REPO).as_posix() in changelog["scripts"], changelog, "package paths", "records")
    lineage = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent"):
        audit.check(f"lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage, kind, "present", "records")
    audit.check("lineage parent", "runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split/" in lineage, PARENT_EXPLORATION, "present", "records")
    if DEFAULT_OUTPUT.is_file():
        audit.check("lineage integrated", f"runs/2026-08-04-integrated-{SLUG}/" in lineage, "integrated", "present", "records")
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    audit.check("surface gate non-load-bearing", SURFACE_GATE in gates and "non-load-bearing" in gates.lower(), SURFACE_GATE, "open non-load-bearing", "records")
    audit.check("next gate registered", NEXT_GATE in gates, NEXT_GATE, "registered", "records")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in manifest["reused_negative_ids"]:
        audit.check(f"reused negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")

    positive_scope = (
        "new_plane_Wick_volume_coherent_Q3_extension",
        "strong_radial_Q3_coercivity_used",
        "finite_component_GRS_Gaussian_conditioning",
        "finite_component_GRS_uniform_subdominant_coupling",
        "all_sixteen_full_half_boundary_pressure_density_limits",
        "half_periodic_plane_Wick_pressure_limit",
        "periodic_ground_energy_density_limit",
        "strict_positive_centered_reference_density",
        "periodic_zero_temperature_specific_KL_limit",
        "joint_scalar_van_Hove_limit",
        "both_iterated_scalar_density_limits_equal",
        "scalar_shift_invariant_gap",
        "periodic_sharp_density_difference_vanishes",
    )
    false_scope = (
        "periodic_sharp_surface_pairing_uniform_in_cutoff_volume_and_interpolation",
        "O_boundary_log_partition_comparison",
        "O1_periodic_sharp_ground_energy_difference",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
        "phase_transition_or_phase_uniqueness",
        "zero_temperature_state_limit",
        "ground_vector_limit",
        "uniform_spectral_gap",
        "correlation_function_limit_interchange",
        "full_noncommutative_infinite_volume_local_algebra",
        "interacting_Hadamard_or_microlocal_spectrum",
        "original_fixed_raw_CL8_family",
        "original_3D_Q3LOCK_parent",
        "physical_light_speed_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    )
    for key in positive_scope:
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("exact scope keyset", set(manifest["scope"]) == set(positive_scope) | set(false_scope), sorted(manifest["scope"]), sorted(set(positive_scope) | set(false_scope)), "scope")
    audit.check("surface remains open", "OPEN BUT NON-LOAD-BEARING" in manifest["stronger_surface_boundary"]["status"], manifest["stronger_surface_boundary"]["status"], "open non-load-bearing", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT, PRIMARY_STORED, INDEPENDENT_STORED):
        audit.check(f"catalog {path.name}", path.relative_to(REPO).as_posix() in catalog, path.relative_to(REPO).as_posix(), "catalogued", "generated")
    for token in (EXPLORATION_ID, NEXT_GATE, MANIFEST.name, CERTIFICATE.name, *REUSED_NEGATIVE_IDS):
        audit.check(f"proof map {token}", token in proof_map, token, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": NEXT_GATE,
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
        },
        "child_summaries": {key: {"passed": value[0], "total": value[1]} for key, value in summaries.items()},
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
