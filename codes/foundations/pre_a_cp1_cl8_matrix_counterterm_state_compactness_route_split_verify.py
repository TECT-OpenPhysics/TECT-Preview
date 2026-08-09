#!/usr/bin/env python3
"""Integrated verifier for the CL8 matrix-counterterm compactness route split."""

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
SLUG = "pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split"
CANDIDATE_ID = "PA-CP1-CL8-MATRIX-COUNTERTERM-STATE-COMPACTNESS-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-UNIFORM-COERCIVE-SHIFT-WEAKSTAR-SUBNET-CUT-DEFECT-IDENTITY-REGULARITY-AND-DYNAMICS-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-ABSTRACT-COMPACTNESS-ONLY-REGULAR-CONTINUUM-STATE",
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-EXACT-DYNAMICS-EQUIVARIANCE",
    "NG-2026-08-04-PRE-A-CP1-CL8-POINTWISE-STABILITY-GAUSSIAN-TRIAL-UNIFORM-ENERGY",
)
EXPLORATION_ID = "EXP-000765"
PARENT_IDS = (
    "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-STATE-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
)
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
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def child_summary(stdout: str) -> dict[str, int]:
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", stdout)
    if match is None:
        raise AssertionError(f"unexpected child output: {stdout!r}")
    return {"passed": int(match.group(1)), "total": int(match.group(2))}


def exploration_record(exploration_id: str) -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == exploration_id:
            return record
    raise AssertionError(f"missing {exploration_id}")


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-prea-matrix-compactness-") as directory:
        root = Path(directory)
        primary, primary_stdout = run_child(PRIMARY, root / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, root / "independent.json")
    summaries = {"primary": child_summary(primary_stdout), "independent": child_summary(independent_stdout)}

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration identity", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent identities", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], list(PARENT_IDS), "identity")
    audit.check("negative identities", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    for name, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{name} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "child")
        audit.check(f"{name} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "child")
        audit.check(f"{name} parents", tuple(child["parent_ids"]) == PARENT_IDS, child["parent_ids"], list(PARENT_IDS), "child")
        audit.check(f"{name} negatives", tuple(child["negative_ids"]) == NEGATIVE_IDS, child["negative_ids"], list(NEGATIVE_IDS), "child")
        audit.check(f"{name} verdict", child["verdict"] == manifest["verdict"], child["verdict"], manifest["verdict"], "child")
        audit.check(f"{name} scope", child["scope"] == manifest["scope"], "equal", "manifest scope", "child")
        audit.check(f"{name} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "freshness")
        for parent_file in PARENT_FILES:
            audit.check(f"{name} parent hash {Path(parent_file).name}", child["source_sha256"][parent_file] == sha256(REPO / parent_file), child["source_sha256"][parent_file], sha256(REPO / parent_file), "freshness")
        audit.check(f"{name} assertions", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "child")
        audit.check(f"{name} command summary", summaries[name] == child["assertion_summary"], summaries[name], child["assertion_summary"], "child")

    primary_spectrum = dict(zip((str(value) for value in primary["derived"]["Q3_spectrum"]["eigenvalues"]), primary["derived"]["Q3_spectrum"]["multiplicities"]))
    audit.check("Q3 spectrum cross agreement", primary_spectrum == independent["derived"]["Q3_spectrum"], primary_spectrum, independent["derived"]["Q3_spectrum"], "cross")
    audit.check("Walsh stiffness cross agreement", primary["derived"]["counterterm_fixture"]["kappa"] == independent["derived"]["Walsh_stiffness"], primary["derived"]["counterterm_fixture"]["kappa"], independent["derived"]["Walsh_stiffness"], "cross")
    shift_pairs = (("b_iso", "b"), ("epsilon_iso", "isotropic"), ("alpha", "alpha"), ("beta", "beta"), ("epsilon_aniso", "anisotropic"))
    for primary_key, independent_key in shift_pairs:
        audit.check(f"counterterm cross {primary_key}", str(primary["derived"]["counterterm_fixture"][primary_key]) == str(independent["derived"]["coercive_shifts"][independent_key]), primary["derived"]["counterterm_fixture"][primary_key], independent["derived"]["coercive_shifts"][independent_key], "cross")
    audit.check("sharpness cross agreement", {key: str(value) for key, value in primary["derived"]["sharpness_fixture"].items()} == independent["derived"]["sharpness"], primary["derived"]["sharpness_fixture"], independent["derived"]["sharpness"], "cross")
    primary_gap = primary["derived"]["Gaussian_gap_fixture"]
    independent_gap = independent["derived"]["singlet_Gaussian"]
    for key in ("minimum", "literal_singlet_mean", "full_reference_mean", "global_gap_lower_bound"):
        audit.check(f"Gaussian gap cross {key}", str(primary_gap[key]) == str(independent_gap[key]), primary_gap[key], independent_gap[key], "cross")
    audit.check("distance cross agreement", primary["derived"]["distance_fixture"] == independent["derived"]["entanglement_distance"], primary["derived"]["distance_fixture"], independent["derived"]["entanglement_distance"], "cross")
    audit.check("dynamic force cross agreement", primary["derived"]["dynamic_force_fixture"]["at_X1_Y1"] == independent["derived"]["dynamic_fixture"]["force_at_X1_Y1"], primary["derived"]["dynamic_force_fixture"], independent["derived"]["dynamic_fixture"], "cross")
    audit.check("dynamic zero cross agreement", primary["derived"]["dynamic_force_fixture"]["at_X1_Y0"] == independent["derived"]["dynamic_fixture"]["force_at_X1_Y0"], primary["derived"]["dynamic_force_fixture"], independent["derived"]["dynamic_fixture"], "cross")
    audit.check("squeezed determinant independent", all(int(q.split("/")[0]) * int(p.split("/")[0]) * 4 == int(q.split("/")[1] if "/" in q else 1) * int(p.split("/")[1] if "/" in p else 1) for q, p in independent["derived"]["squeezed_covariances"]), independent["derived"]["squeezed_covariances"], "determinant 1/4", "cross")

    required_fragments = {
        "primary": (
            "parent Wick matrix convention",
            "lambda-zero isotropic route",
            "general Gaussian gap leading coefficient",
            "three-regulator Nyquist transitivity",
            "predual chart restriction nontrivial",
            "cut and bulk dual norms agree",
            "collective mixed derivative derived",
            "weighted Holder fourth-power equality",
            "scope false: Pre_A_complete",
        ),
        "independent": (
            "parent Wick matrix convention",
            "lambda-zero isotropic route",
            "general-gap finite difference",
            "three-regulator old-pair transitivity",
            "predual chart restriction",
            "cut and bulk dual norms agree",
            "dynamic mixed derivative",
            "weighted Holder equality",
            "scope false: Pre_A_complete",
        ),
    }
    for child_name, child in (("primary", primary), ("independent", independent)):
        names = {row["name"] for row in child["assertions"]}
        for fragment in required_fragments[child_name]:
            audit.check(f"{child_name} coverage {fragment}", any(fragment in name for name in names), fragment, "present", "coverage")

    independent_source = INDEPENDENT.read_text(encoding="utf-8").lower()
    audit.check("independent has no SymPy", "import sympy" not in independent_source, "absent", "absent", "independence")
    audit.check("independent has no NumPy", "import numpy" not in independent_source, "absent", "absent", "independence")
    primary_module_name = SLUG.replace("-", "_")
    audit.check("independent does not import primary", primary_module_name not in independent_source.replace(primary_module_name + "_independent", ""), "absent", "absent", "independence")
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"), filename=str(INDEPENDENT))
    imported_roots: set[str] = set()
    dynamic_import_calls: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec"}:
            dynamic_import_calls.add(node.func.id)
    banned_imports = {"sympy", "numpy", "importlib", "runpy", "subprocess", primary_module_name}
    audit.check("independent AST import firewall", imported_roots.isdisjoint(banned_imports), sorted(imported_roots & banned_imports), "empty", "independence")
    audit.check("independent AST dynamic-execution firewall", not dynamic_import_calls, sorted(dynamic_import_calls), "empty", "independence")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    audit.check("stored primary fresh", PRIMARY_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(primary), sha256(PRIMARY_STORED), hashlib.sha256(canonical_bytes(primary)).hexdigest(), "stored")
    audit.check("stored independent fresh", INDEPENDENT_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(independent), sha256(INDEPENDENT_STORED), hashlib.sha256(canonical_bytes(independent)).hexdigest(), "stored")

    anchors = (
        "section-2-authorities-and-scope",
        "section-3-matrix-counterterm-convention",
        "section-4-uniform-coercive-shift",
        "section-5-finite-state-and-moment-reduction",
        "section-6-ground-entanglement-distance",
        "section-7-abstract-compatible-subnet",
        "section-8-matched-reference-cut-square",
        "section-8a-natural-dynamics-no-go",
        "section-9-regularity-no-go",
        "section-10-positive-regularity-gate",
        "section-11-constructive-positive-branch",
        "section-13-adversarial-review",
        "section-15-next-gate",
    )
    for anchor in anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate, anchor, "present", "certificate")
    certificate_phrases = (
        "full eight-component reference Gaussian",
        "iota_(M,2M,*)",
        "Bare `Tr_add P_(0,2M)` is generally wrong",
        "normalizer theorem for type-I tensor factors",
        "partial_X^2\\partial_Y^2U_N={6g\\over L}>0",
        "cubic force term",
        "registered unitary anchors",
        "finite Euclidean-time circle targets a `beta`-KMS state",
        "finite-torus construction alone cannot establish a thermodynamic phase transition",
        "does not identify a physical reference or energy sign",
    )
    for phrase in certificate_phrases:
        audit.check(f"certificate phrase {phrase[:35]}", phrase in certificate_flat, phrase, "present", "certificate")
    package_files = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
    non_ascii = {
        str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127})
        for path in package_files
    }
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"negative registered {negative_id}", f"### {negative_id} " in negative_text, negative_id, "detailed entry", "records")
    index_text = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index registered", MANIFEST.name in index_text and CERTIFICATE.name in index_text, [MANIFEST.name, CERTIFICATE.name], "both", "records")
    exploration = exploration_record(EXPLORATION_ID)
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration claim nonbearing", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "empty results", "records")
    audit.check("exploration negatives", tuple(exploration["formal_refs"].get("negatives", [])) == NEGATIVE_IDS, exploration["formal_refs"], list(NEGATIVE_IDS), "records")
    audit.check("exploration continues prior route", any(item.get("id") == "EXP-000764" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000764", "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", EXPLORATION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, EXPLORATION_ID, "TODO and gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", EXPLORATION_ID in changelog_text and MANIFEST.name in changelog_text, EXPLORATION_ID, "changelog and manifest", "records")
    lineage_text = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent", "integrated"):
        audit.check(f"C6 lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage_text, kind, "run", "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("C6 advancement false", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "claim_firewall")
    audit.check("Pre-A false", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "claim_firewall")
    audit.check("below empty space false", manifest["scope"]["below_empty_space_comparison"] is False, manifest["scope"]["below_empty_space_comparison"], False, "claim_firewall")

    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog manifest", MANIFEST.name in catalog, MANIFEST.name, "catalogued", "generated")
    audit.check("catalog certificate", CERTIFICATE.name in catalog, CERTIFICATE.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map, EXPLORATION_ID, "mapped", "generated")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"proof map negative {negative_id}", negative_id in proof_map, negative_id, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "status": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
        },
        "child_summaries": summaries,
        "cross_oracles": {
            "Q3_spectrum": primary_spectrum,
            "Walsh_stiffness": independent["derived"]["Walsh_stiffness"],
            "coercive_shifts": independent["derived"]["coercive_shifts"],
            "Gaussian_gap": independent_gap,
            "distance": independent["derived"]["entanglement_distance"],
            "dynamic": independent["derived"]["dynamic_fixture"],
        },
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
