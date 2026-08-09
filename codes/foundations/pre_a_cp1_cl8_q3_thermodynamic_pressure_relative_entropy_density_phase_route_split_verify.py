#!/usr/bin/env python3
"""Integrated verifier for the Q3 thermodynamic pressure/entropy theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-thermodynamic-pressure-relative-entropy-density-phase-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-THERMODYNAMIC-PRESSURE-RELATIVE-ENTROPY-DENSITY-AND-PHASE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FIXED-BETA-VOLUME-COHERENT-NELSON-PRESSURE-SPECIFIC-RELATIVE-ENTROPY-AND-PERIODIC-LOCAL-SCHWINGER-LIMIT"
EXPLORATION_ID = "EXP-000775"
PARENT_EXPLORATION = "EXP-000774"
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
    completed = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=REPO, capture_output=True, text=True, timeout=120)
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
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    with tempfile.TemporaryDirectory(prefix="tect-q3-thermodynamic-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(f"{label} identity", child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID, (child["candidate_id"], child["result_id"]), (CANDIDATE_ID, RESULT_ID), "children")
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

    imported = imports(INDEPENDENT)
    audit.check("independent no primary import", PRIMARY.stem not in imported, sorted(imported), f"not {PRIMARY.stem}", "independence")
    audit.check("independent stdlib only", not ({"sympy", "mpmath", "numpy", "scipy"} & imported), sorted(imported), "stdlib only", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    primary_names = {row["name"] for row in primary["assertions"]}
    independent_names = {row["name"] for row in independent["assertions"]}
    for name in (
        "exact plane-to-torus Wick identity",
        "arbitrary K stability scalar minimum",
        "generic matrix volume coherence",
        "wrong scalar sign mutation",
        "mass-only volume mutation",
        "rectangular covariance exchange N7",
        "image covariance exchange R7",
        "circle correction decays with L",
        "cylinder image decomposition L2.1",
        "cylinder limit tends a_beta",
        "torus scalar tends dual circle scalar",
        "two-dimensional Green coefficient flux",
        "Nelson dual trace rate",
        "raw pressure scalar shift law",
        "raw pressure sign mutable",
        "full scalar density factor ledger",
        "finite KL identity",
        "finite KL scalar invariance",
        "KL direction mutation",
        "strict Bregman ground gap",
        "Q3 pure quartic coefficient",
        "zero-mode four-creation normalization",
        "Q3 dual amplitude factor derivation",
        "Q3 dual four-particle amplitude",
        "form Rayleigh strictness arbitrary B",
        "specific KL length composition",
        "specific KL beta factor",
        "dual ground projection convergence",
        "exponential spatial clustering fixture",
        "trace-normalized connected transfer limit",
        "scope firewall physical_empty_space_reference",
    ):
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in (
        "independent exact plane-torus Wick identity",
        "independent arbitrary K stability minimum",
        "independent matrix volume coherence",
        "independent scalar sign mutation",
        "independent mass-only volume mutation",
        "independent exact image-radius exchange",
        "independent Bessel-integral exchange",
        "independent circle correction decay",
        "independent cylinder decomposition L1.9",
        "independent cylinder limit",
        "independent scalar cylinder limit",
        "independent Green coefficient flux",
        "independent Nelson trace rate",
        "independent raw pressure shift",
        "independent raw sign mutation",
        "independent full scalar factor ledger",
        "independent free-to-interacting KL identity",
        "independent KL scalar invariance",
        "independent KL direction mutation",
        "independent strict Bregman density",
        "independent Q3 pure quartic coefficient",
        "independent zero-mode normalization squared",
        "independent Q3 amplitude factor derivation",
        "independent Q3 dual amplitude squared",
        "independent form Rayleigh strictness",
        "independent specific KL length composition",
        "independent specific KL beta factor",
        "independent ground projection",
        "independent exponential clustering",
        "independent trace-normalized connected limit",
        "independent scope firewall physical_empty_space_reference",
    ):
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    audit.check("cross Q3 edges", len(primary["derived"]["Q3"]["edges"]) == independent["derived"]["Q3"]["edges"] == 12, (len(primary["derived"]["Q3"]["edges"]), independent["derived"]["Q3"]["edges"]), 12, "cross")
    audit.check("cross image differences positive", primary["derived"]["coherence"]["images"][-1]["forward"] > 0.0 and independent["derived"]["coherence"]["image"] > 0.0, (primary["derived"]["coherence"]["images"][-1]["forward"], independent["derived"]["coherence"]["image"]), "positive", "cross")
    audit.check("cross covariance fixtures distinct", primary["derived"]["coherence"]["rectangular"] != independent["derived"]["coherence"]["covariance"], "distinct", "distinct", "cross")
    audit.check("cross transfer rates positive", primary["derived"]["pressure"]["transfer"][-1]["rate"] > 0.0 and independent["derived"]["pressure"]["rates"][-1]["rate"] > 0.0, (primary["derived"]["pressure"]["transfer"][-1], independent["derived"]["pressure"]["rates"][-1]), "positive fixtures", "cross")
    audit.check("cross raw sign mutation", primary["derived"]["pressure"]["raw"] > 0 > primary["derived"]["pressure"]["shifted"] and independent["derived"]["pressure"]["raw"] > 0 > independent["derived"]["pressure"]["shifted"], (primary["derived"]["pressure"], independent["derived"]["pressure"]), "both signs", "cross")
    audit.check("cross KL positive", primary["derived"]["entropy"]["divergence"] > 0.0 and independent["derived"]["entropy"]["KL"] > 0.0, (primary["derived"]["entropy"]["divergence"], independent["derived"]["entropy"]["KL"]), "positive", "cross")
    audit.check("cross KL identities", abs(primary["derived"]["entropy"]["divergence"] - primary["derived"]["entropy"]["identity"]) < 2e-15 and abs(independent["derived"]["entropy"]["KL"] - independent["derived"]["entropy"]["formula"]) < 2e-15, (primary["derived"]["entropy"], independent["derived"]["entropy"]), "exact numeric", "cross")
    audit.check("cross strict Bregman", primary["derived"]["entropy"]["Bregman"] > 0.0 and independent["derived"]["entropy"]["Bregman"] > 0.0, (primary["derived"]["entropy"]["Bregman"], independent["derived"]["entropy"]["Bregman"]), "positive", "cross")
    audit.check("cross KL directions differ", abs(primary["derived"]["entropy"]["divergence"] - primary["derived"]["entropy"]["reverse"]) > 1e-3 and abs(independent["derived"]["entropy"]["KL"] - independent["derived"]["entropy"]["reverse"]) > 1e-3, (primary["derived"]["entropy"], independent["derived"]["entropy"]), "different directions", "cross")
    audit.check("cross specific beta factors positive", primary["derived"]["entropy"]["density"][-1]["D_per_area"] > 0.0 and independent["derived"]["entropy"]["density"][-1]["D_per_area"] > 0.0, (primary["derived"]["entropy"]["density"][-1], independent["derived"]["entropy"]["density"][-1]), "positive", "cross")
    audit.check("cross dual gaps", primary["derived"]["state"]["gap"] > 0.0 and independent["derived"]["state"]["gap"] > 0.0, (primary["derived"]["state"]["gap"], independent["derived"]["state"]["gap"]), "positive", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "Plane-to-torus covariance and exact volume coherence",
        "Nelson coordinate exchange and the pressure limit",
        "Finite-volume relative entropy identity",
        "Strictness from the Q3 four-particle witness",
        "specific relative entropy per Euclidean area",
        "Periodic bounded-local Schwinger limit",
        "full noncommutative infinite-volume KMS algebra",
        "not convergence of global density matrices",
        "raw pressure or vacuum-energy density",
        "global Radon--Nikodym derivative",
        "zero-temperature thermodynamic ground-energy density",
        "Pre-A",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index", MANIFEST.name in index and CERTIFICATE.name in index, (MANIFEST.name, CERTIFICATE.name), "indexed", "records")
    exploration = exploration_record()
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration no result card", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "claim nonbearing", "records")
    audit.check("exploration parent", any(item.get("id") == PARENT_EXPLORATION and item.get("relation") in {"continues", "composes"} for item in exploration.get("related", [])), exploration.get("related"), PARENT_EXPLORATION, "records")
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
    for negative_id in manifest["reused_negative_ids"]:
        audit.check(f"reused negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")

    audit.check("analytic proof label", manifest["verification"]["proof_grade"].startswith("ANALYTIC"), manifest["verification"]["proof_grade"], "ANALYTIC", "scope")
    audit.check("raw sign explicitly false", manifest["scope"]["raw_relative_pressure_sign_gauge_invariant"] is False, manifest["scope"]["raw_relative_pressure_sign_gauge_invariant"], False, "scope")
    audit.check("specific KL explicitly true", manifest["scope"]["strict_positive_specific_relative_entropy_density"] is True, manifest["scope"]["strict_positive_specific_relative_entropy_density"], True, "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    for key in (
        "raw_relative_pressure_sign_gauge_invariant",
        "arbitrary_L_dependent_K_and_scalar_family",
        "original_fixed_raw_CL8_family",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
        "global_infinite_volume_Radon_Nikodym_density",
        "finite_total_infinite_volume_relative_entropy",
        "all_boundary_condition_state_uniqueness",
        "periodic_beta_KMS_limit",
        "full_noncommutative_infinite_volume_local_algebra",
        "beta_to_infinity_L_to_infinity_interchange",
        "zero_temperature_ground_energy_density",
        "spontaneous_symmetry_breaking_or_phase_transition",
        "interacting_Hadamard_or_microlocal_spectrum",
        "original_3D_Q3LOCK_parent",
        "physical_light_speed_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    ):
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog package", MANIFEST.name in catalog and CERTIFICATE.name in catalog, MANIFEST.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map, EXPLORATION_ID, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": [],
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
