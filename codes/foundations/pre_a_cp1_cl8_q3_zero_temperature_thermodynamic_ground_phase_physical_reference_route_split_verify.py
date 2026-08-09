#!/usr/bin/env python3
"""Integrated verifier for the sharp-cutoff Q3 theorem and periodic bridge gate."""

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


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-ZERO-TEMPERATURE-THERMODYNAMIC-GROUND-PHASE-AND-PHYSICAL-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-SHARP-CUTOFF-GRS-MONOTONE-STRICT-VACUUM-DENSITY-AND-PERIODIC-BRIDGE-REDUCTION"
NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-FINITE-CIRCLE-WITNESS-ZERO-TEMPERATURE-DENSITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-VOLUME-UI-PERIODIC-SHARP-SURFACE-PAIRING",
]
EXPLORATION_ID = "EXP-000777"
PARENT_EXPLORATION = "EXP-000776"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
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
    completed = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=REPO, capture_output=True, text=True, timeout=180)
    if completed.returncode:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", completed.stdout.strip())
    if match is None:
        raise AssertionError(completed.stdout)
    return json.loads(output.read_text(encoding="utf-8")), (int(match.group(1)), int(match.group(2)))


def exploration_record() -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == EXPLORATION_ID:
            return record
    raise AssertionError(f"missing {EXPLORATION_ID}")


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    result |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    with tempfile.TemporaryDirectory(prefix="tect-q3-zero-temperature-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(f"{label} identity", child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID, (child["candidate_id"], child["result_id"]), (CANDIDATE_ID, RESULT_ID), "children")
        audit.check(f"{label} negatives", child["negative_ids"] == NEGATIVE_IDS, child["negative_ids"], NEGATIVE_IDS, "children")
        audit.check(f"{label} scope", child["scope"] == manifest["scope"], child["scope"], manifest["scope"], "children")
        audit.check(f"{label} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical(primary_stored) == canonical(primary), sha256(PRIMARY_STORED), "fresh", "stored")
    audit.check("stored independent fresh", canonical(independent_stored) == canonical(independent), sha256(INDEPENDENT_STORED), "fresh", "stored")
    for label, child, script in (("primary", primary, PRIMARY), ("independent", independent, INDEPENDENT)):
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(script), child["source_sha256"]["script"], sha256(script), "stored")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "stored")
        audit.check(f"{label} certificate hash", child["source_sha256"]["certificate"] == sha256(CERTIFICATE), child["source_sha256"]["certificate"], sha256(CERTIFICATE), "stored")

    independent_imports = imports(INDEPENDENT)
    audit.check("independent no primary import", PRIMARY.stem not in independent_imports, sorted(independent_imports), f"not {PRIMARY.stem}", "independence")
    audit.check("independent stdlib only", not ({"sympy", "mpmath", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "stdlib only", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    primary_names = {row["name"] for row in primary["assertions"]}
    independent_names = {row["name"] for row in independent["assertions"]}
    for name in (
        "Q3 pure quartic coefficient",
        "mixed-axis counterexample has flat ray",
        "Q3 onsite removes flat ray",
        "Q3 arbitrary quadratic stability",
        "spectral Holder probability inequality a=0.47",
        "GRS alpha monotone fixture",
        "GRS energy scaling implication",
        "ground spectral squeeze",
        "sharp Q3 four-particle norm positive",
        "sharp two-vector ground strictness",
        "formal surface bound would vanish per area",
        "formal O1 energy bridge would vanish per length",
        "finite fixture cannot certify uniform surface pairing",
        "circle scalar tends plane scalar",
        "conditional periodic centered energy fixture",
        "conditional zero-temperature specific KL fixture",
        "zero-temperature gap scalar invariant",
        "raw zero-temperature sign mutable",
        "beta-L scalar density symmetry",
        "conditional joint scalar van Hove fixture",
        "finite-circle witness subextensive",
        "K0 fourth-power integral",
        "eight-channel curvature factor",
        "finite-block strict Jensen fixture",
        "formal chessboard dissemination fixture",
    ):
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in (
        "independent pure quartic coefficient",
        "independent Nagoji flat-axis mutation",
        "independent spectral Holder inequality",
        "independent GRS alpha implication",
        "independent sharp spectral squeeze",
        "independent fourth-chaos norm",
        "independent strict ground Rayleigh",
        "independent finite open-periodic covariance fixture bounded",
        "independent finite covariance-density fixture decreases",
        "independent formal surface scaling implication",
        "independent formal O1 bridge scaling implication",
        "independent conditional zero-temperature gap fixture",
        "independent scalar gap invariance",
        "independent raw sign mutation",
        "independent conditional joint van Hove fixture",
        "independent finite-circle witness no uniform density",
        "independent eight-channel curvature algebra",
        "independent finite-block Jensen fixture",
        "independent formal chessboard dissemination fixture",
    ):
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    audit.check("cross Q3 graph", len(primary["derived"]["Q3"]["edges"]) == independent["derived"]["Q3"]["edges"] == 12, (len(primary["derived"]["Q3"]["edges"]), independent["derived"]["Q3"]["edges"]), 12, "cross")
    audit.check("cross fourth witness positive", float(primary["derived"]["strictness"]["witness_norm_squared"]) > 0.0 and independent["derived"]["strictness"]["fourth_norm"] > 0.0, (primary["derived"]["strictness"], independent["derived"]["strictness"]), "positive", "cross")
    audit.check("cross strict Rayleigh", primary["derived"]["strictness"]["rayleigh_ground"] < 0.0 and independent["derived"]["strictness"]["Rayleigh"] < 0.0, (primary["derived"]["strictness"]["rayleigh_ground"], independent["derived"]["strictness"]["Rayleigh"]), "negative", "cross")
    audit.check("cross formal boundary fixtures decrease", primary["derived"]["boundary"]["rows"][-1]["energy_over_length"] < primary["derived"]["boundary"]["rows"][0]["energy_over_length"] and independent["derived"]["boundary"]["surface"][-1]["ground_error_per_length"] < independent["derived"]["boundary"]["surface"][0]["ground_error_per_length"], "both decrease conditionally", "both decrease conditionally", "cross")
    audit.check("cross conditional zero-temperature fixtures positive", primary["derived"]["zero_temperature"]["beta"][-1]["specific_KL"] > 0.0 and independent["derived"]["zero_temperature"]["beta"][-1]["gap"] > 0.0, (primary["derived"]["zero_temperature"]["beta"][-1], independent["derived"]["zero_temperature"]["beta"][-1]), "positive fixtures only", "cross")
    audit.check("cross curvature positive", float(primary["derived"]["curvature"]["lower"]) > 0.0 and independent["derived"]["curvature"]["lower"] > 0.0, (primary["derived"]["curvature"]["lower"], independent["derived"]["curvature"]["lower"]), "positive", "cross")
    audit.check("cross finite chessboard fixtures strict", primary["derived"]["chessboard"]["local_partition"] > 1.0 and independent["derived"]["chessboard"]["block_partition"] > 1.0, (primary["derived"]["chessboard"]["local_partition"], independent["derived"]["chessboard"]["block_partition"]), ">1 fixtures only", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "Sharp-cutoff line Hamiltonians",
        "Open-rectangle Feynman--Kac and Nelson symmetry",
        "component-blind GRS monotonicity proof",
        "Strictness from a local Q3 fourth-chaos vector",
        "Periodic-sharp surface-pairing reduction and open gate",
        "Gaussian covariance interpolation",
        "Conditional periodic zero-temperature composition and scalar ledger",
        "scalar densities only",
        "Phase and physical-reference firewall",
        "physical empty space",
        "do not certify the open uniform estimate",
        "Pre-A",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index", MANIFEST.name in index and CERTIFICATE.name in index, (MANIFEST.name, CERTIFICATE.name), "indexed", "records")
    exploration = exploration_record()
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration no result card", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "claim nonbearing", "records")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"exploration negative {negative_id}", negative_id in exploration["formal_refs"].get("negatives", []), exploration["formal_refs"], negative_id, "records")
    audit.check("exploration supersedes parent", any(item.get("id") == PARENT_EXPLORATION and item.get("relation") == "supersedes" for item in exploration.get("related", [])), exploration.get("related"), PARENT_EXPLORATION, "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    changelog = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("TODO record", EXPLORATION_ID in todo and manifest["gate_resolution"]["next_gate"] in todo, EXPLORATION_ID, "present", "records")
    audit.check("changelog record", EXPLORATION_ID in changelog and MANIFEST.name in changelog, EXPLORATION_ID, "present", "records")
    lineage = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent"):
        audit.check(f"lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage, kind, "present", "records")
    if DEFAULT_OUTPUT.is_file():
        audit.check("lineage integrated", f"runs/2026-08-04-integrated-{SLUG}/" in lineage, "integrated", "present", "records")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"new negative registered {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")
    for negative_id in manifest["reused_negative_ids"]:
        audit.check(f"reused negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")

    audit.check("analytic proof label", manifest["verification"]["proof_grade"].startswith("ANALYTIC"), manifest["verification"]["proof_grade"], "ANALYTIC", "scope")
    audit.check("strict sharp-cutoff scope", manifest["scope"]["strict_positive_centered_reference_density"] is True, "strict sharp density", True, "scope")
    audit.check("periodic bridge firewall", manifest["scope"]["periodic_zero_temperature_specific_KL_limit"] is False and manifest["scope"]["joint_scalar_van_Hove_limit"] is False and manifest["scope"]["both_iterated_scalar_density_limits_equal"] is False and manifest["scope"]["periodic_sharp_surface_pairing_uniform_in_cutoff_volume_and_interpolation"] is False and manifest["scope"]["periodic_dyadic_positive_pressure_liminf"] is False and manifest["scope"]["periodic_zero_temperature_limit_reduced_to_surface_pairing"] is True, "periodic limits and dyadic liminf false; reduction true", "periodic limits and dyadic liminf false; reduction true", "scope")
    audit.check("state limit firewall", manifest["scope"]["zero_temperature_state_limit"] is False and manifest["scope"]["ground_vector_limit"] is False and manifest["scope"]["uniform_spectral_gap"] is False, "state/gap false", False, "scope")
    audit.check("physical reference firewall", manifest["scope"]["physical_empty_space_reference"] is False and manifest["scope"]["absolute_vacuum_energy_fixed"] is False, "physical/absolute false", False, "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    audit.check("Pre-A remains open", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "scope")
    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog package", MANIFEST.name in catalog and CERTIFICATE.name in catalog, MANIFEST.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map, EXPLORATION_ID, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": NEGATIVE_IDS,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
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
