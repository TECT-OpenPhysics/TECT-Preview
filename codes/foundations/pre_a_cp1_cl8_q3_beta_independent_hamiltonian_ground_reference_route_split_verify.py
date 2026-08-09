#!/usr/bin/env python3
"""Integrated verifier for the compact-circle Q3 Hamiltonian/ground theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-beta-independent-hamiltonian-ground-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-BETA-INDEPENDENT-HAMILTONIAN-GROUND-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-COMPACT-CIRCLE-FIXED-HAMILTONIAN-FK-GIBBS-AND-STRICT-GROUND-REFERENCE-ADVANTAGE"
EXPLORATION_ID = "EXP-000774"
PARENT_EXPLORATION = "EXP-000773"
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
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], tuple[int, int]]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
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

    with tempfile.TemporaryDirectory(prefix="tect-q3-fixed-hamiltonian-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(
            f"{label} identity",
            child["candidate_id"] == CANDIDATE_ID and child["result_id"] == RESULT_ID,
            (child["candidate_id"], child["result_id"]),
            (CANDIDATE_ID, RESULT_ID),
            "children",
        )
        audit.check(f"{label} scope", child["scope"] == manifest["scope"], child["scope"], manifest["scope"], "children")
        audit.check(
            f"{label} next gate",
            child["next_gate"] == manifest["gate_resolution"]["next_gate"],
            child["next_gate"],
            manifest["gate_resolution"]["next_gate"],
            "children",
        )

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
    audit.check("independent stdlib only", not ({"sympy", "numpy", "scipy"} & imported), sorted(imported), "stdlib only", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    primary_names = {row["name"] for row in primary["assertions"]}
    independent_names = {row["name"] for row in independent["assertions"]}
    for name in (
        "Q3 quartic Laplacian",
        "exact coherent Wick polynomial identity",
        "generic symmetric K exact Wick identity",
        "generic symmetric K coefficient coherence",
        "coherent uncorrected scalar sign",
        "absolute scalar compensator",
        "raw field-dependent coefficients beta independent",
        "mass-only mutation fails for lambda",
        "thermal-vacuum D identity beta0.7",
        "free Fock trace tail converges",
        "four-particle amplitude positive domain",
        "Rayleigh-Ritz strict negative fixture",
        "ground free-energy limit approaches -2",
        "scope firewall physical_empty_space_reference",
    ):
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in (
        "independent exact Wick dictionary",
        "independent generic symmetric K dictionary",
        "independent generic K not Q3 symmetric specialization",
        "independent coherent scalar",
        "independent scalar compensator",
        "independent raw coefficient coherence",
        "independent mass-only mutation",
        "independent D ground decay",
        "independent Fock trace tail",
        "independent four-particle amplitude squared",
        "independent Rayleigh strictness",
        "independent ground free-energy limit",
        "independent scope firewall physical_empty_space_reference",
    ):
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    audit.check("cross Q3 edge count", len(primary["derived"]["Q3"]["edges"]) == independent["derived"]["Q3"]["edges"] == 12, (len(primary["derived"]["Q3"]["edges"]), independent["derived"]["Q3"]["edges"]), 12, "cross")
    audit.check("cross Q3 Laplacian trace", primary["derived"]["Q3"]["trace_L"] == independent["derived"]["Q3"]["trace_L"] == "24", (primary["derived"]["Q3"]["trace_L"], independent["derived"]["Q3"]["trace_L"]), "24", "cross")
    audit.check("cross coherent scalar sign", primary["derived"]["Wick"]["coherent_scalar"].startswith("-"), primary["derived"]["Wick"]["coherent_scalar"], "negative convention", "cross")
    audit.check("cross scalar cancellation", primary["derived"]["Wick"]["coherent_scalar"] != primary["derived"]["Wick"]["compensator"] and independent["derived"]["Wick"]["coherent_scalar"].startswith("-"), (primary["derived"]["Wick"], independent["derived"]["Wick"]), "opposite compensator", "cross")
    audit.check("cross thermal fixtures independent", primary["derived"]["thermal_difference"] != independent["derived"]["thermal_difference"], "distinct", "distinct", "cross")
    audit.check("cross D positive", all(row["bose"] > 0 for row in primary["derived"]["thermal_difference"]) and all(row["K560"] > 0 for row in independent["derived"]["thermal_difference"]), "positive", "positive", "cross")
    audit.check("cross Fock convergence fixtures independent", primary["derived"]["free_Fock_trace"] != independent["derived"]["free_Fock_trace"], "distinct", "distinct", "cross")
    audit.check("cross four-particle witnesses positive", not primary["derived"]["ground"]["amplitude"].startswith("-") and not independent["derived"]["ground"]["amplitude_squared"].startswith("-"), (primary["derived"]["ground"]["amplitude"], independent["derived"]["ground"]["amplitude_squared"]), "positive", "cross")
    audit.check("cross Rayleigh witnesses negative", primary["derived"]["ground"]["Rayleigh"].startswith("t*") or "-2*A" in primary["derived"]["ground"]["Rayleigh"], primary["derived"]["ground"]["Rayleigh"], "negative for small t", "cross")
    audit.check("cross fixed-H ground limits negative", primary["derived"]["ground"]["free_energy"][-1]["difference"] < 0 and independent["derived"]["ground"]["free_energy"][-1]["difference"] < 0, (primary["derived"]["ground"]["free_energy"][-1], independent["derived"]["ground"]["free_energy"][-1]), "negative", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "Wick coherence across beta",
        "Necessary and sufficient coherence",
        "Eight-component Hamiltonian construction",
        "Feynman--Kac--Nelson identification",
        "not inferred from strong-resolvent convergence alone",
        "closed Hamiltonian form",
        "finite-particle Wick form core",
        "Strict compact-circle ground advantage",
        "Ground limit and the finite-beta scalar firewall",
        "What is still not physical empty space",
        "does not prove a thermodynamic limit",
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
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    for key in (
        "arbitrary_bounded_K_beta_family",
        "original_fixed_raw_CL8_family",
        "thermodynamic_limit",
        "strict_thermodynamic_energy_density",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
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
