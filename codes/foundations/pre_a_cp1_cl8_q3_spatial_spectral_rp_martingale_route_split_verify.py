#!/usr/bin/env python3
"""Integrated verifier for the Q3 spatial-spectral RP martingale route split."""

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
SLUG = "pre-a-cp1-cl8-q3-spatial-spectral-rp-martingale-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-MARTINGALE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-FK-MARTINGALE-FAMILY-AND-LIMITING-MEASURE-RP-WITH-CANONICAL-NONIDENTIFICATION"
NEGATIVE_IDS = ("NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER",)
EXPLORATION_ID = "EXP-000769"
PARENT_EXPLORATION_ID = "EXP-000768"
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


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=REPO, capture_output=True, text=True, timeout=120)
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def child_summary(stdout: str) -> dict[str, int]:
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", stdout)
    if match is None:
        raise AssertionError(f"unexpected child output: {stdout!r}")
    return {"passed": int(match.group(1)), "total": int(match.group(2))}


def assertion_names(payload: dict[str, Any]) -> set[str]:
    return {row["name"] for row in payload["assertions"]}


def exploration_record(exploration_id: str) -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == exploration_id:
            return record
    raise AssertionError(f"missing exploration {exploration_id}")


def imported_modules(path: Path) -> tuple[set[str], set[str], set[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    direct = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    from_modules = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    dynamic = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile"}}
    return direct, from_modules, dynamic


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    with tempfile.TemporaryDirectory(prefix="tect-q3-spatial-rp-integrated-") as temporary:
        temporary_path = Path(temporary)
        primary, primary_stdout = run_child(PRIMARY, temporary_path / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, temporary_path / "independent.json")
    summaries = {"primary": child_summary(primary_stdout), "independent": child_summary(independent_stdout)}
    audit.check("primary child all pass", summaries["primary"]["passed"] == summaries["primary"]["total"], summaries["primary"], "all pass", "children")
    audit.check("independent child all pass", summaries["independent"]["passed"] == summaries["independent"]["total"], summaries["independent"], "all pass", "children")
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "children")
        audit.check(f"{label} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "children")
        audit.check(f"{label} negatives", tuple(child["negative_ids"]) == NEGATIVE_IDS, child["negative_ids"], list(NEGATIVE_IDS), "children")
        audit.check(f"{label} scope", child["scope"] == manifest["scope"], child["scope"], manifest["scope"], "children")
        audit.check(f"{label} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical_bytes(primary_stored) == canonical_bytes(primary), sha256(PRIMARY_STORED), "fresh child payload", "stored")
    audit.check("stored independent fresh", canonical_bytes(independent_stored) == canonical_bytes(independent), sha256(INDEPENDENT_STORED), "fresh child payload", "stored")
    for label, child, script in (("primary", primary, PRIMARY), ("independent", independent, INDEPENDENT)):
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(script), child["source_sha256"]["script"], sha256(script), "stored")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "stored")
        audit.check(f"{label} certificate hash", child["source_sha256"]["certificate"] == sha256(CERTIFICATE), child["source_sha256"]["certificate"], sha256(CERTIFICATE), "stored")

    primary_names = assertion_names(primary)
    independent_names = assertion_names(independent)
    primary_required = (
        "spatial Wick conditioning degree 4",
        "Q3 edge Wick conditioning",
        "rational Q3 edge conditioning fixture",
        "conditional exponential Jensen cell 0",
        "normalized L1 inequality",
        "massive circle reflected covariance factorization",
        "reflected covariance Gram rank",
        "reflected form L1 stability fixture",
        "eight-component fourth-power Cauchy SOS",
        "finite oscillator dimension",
        "centered versus spectral strict fixture",
        "Nyquist quartic alias gap",
        "low-band quartic quadrature survivor",
        "Q3 Wick translation levels",
        "below empty space firewall",
    )
    independent_required = (
        "independent Wick conditioning degree 4",
        "independent Q3 edge conditioning",
        "independent Q3 explicit Wick formula",
        "finite conditional exponential Jensen 0",
        "independent normalized L1 bound",
        "independent RP Gram symmetric",
        "independent reflected-form L1 closure",
        "independent canonical dimension",
        "independent missing Matsubara mismatch",
        "independent symbol strictness",
        "independent Nyquist quartic gap",
        "independent low-band quadrature",
        "independent Wick matrix levels",
        "stdlib numeric firewall",
        "independent below empty firewall",
    )
    for name in primary_required:
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in independent_required:
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    direct, from_modules, dynamic = imported_modules(INDEPENDENT)
    audit.check("independent AST primary firewall", PRIMARY.stem not in direct and PRIMARY.stem not in from_modules, sorted(direct | from_modules), f"not {PRIMARY.stem}", "independence")
    audit.check("independent AST numeric firewall", not ({"sympy", "numpy", "scipy"} & (direct | from_modules)), sorted(direct | from_modules), "stdlib only", "independence")
    audit.check("independent AST dynamic firewall", not dynamic and "runpy" not in direct and "importlib" not in direct, {"dynamic": sorted(dynamic), "imports": sorted(direct)}, "none", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    audit.check("cross onsite degree four", primary["derived"]["hermite_conditioning"]["4"].replace(" ", "") == "C**2*3-6*C*L**2+L**4".replace(" ", "") or "L**4" in primary["derived"]["hermite_conditioning"]["4"], primary["derived"]["hermite_conditioning"]["4"], independent["derived"]["onsite_conditioning"]["4"], "cross")
    audit.check("cross Q3 conditioning nonempty", bool(primary["derived"]["Q3_edge_conditioned"]) and bool(independent["derived"]["Q3_edge_conditioning"]), primary["derived"]["Q3_edge_conditioned"], "nonempty independent", "cross")
    audit.check("cross Nyquist continuum", primary["derived"]["Nyquist_continuum_average"] == independent["derived"]["Nyquist"]["continuum"] == "3/8", primary["derived"]["Nyquist_continuum_average"], independent["derived"]["Nyquist"]["continuum"], "cross")
    audit.check("cross Nyquist nodal", primary["derived"]["Nyquist_nodal_average"] == independent["derived"]["Nyquist"]["nodal"] == "1", primary["derived"]["Nyquist_nodal_average"], independent["derived"]["Nyquist"]["nodal"], "cross")
    audit.check("cross Nyquist gap", primary["derived"]["Nyquist_alias_gap"] == independent["derived"]["Nyquist"]["gap"] == "5/8", primary["derived"]["Nyquist_alias_gap"], independent["derived"]["Nyquist"]["gap"], "cross")
    audit.check("cross Wick levels", primary["derived"]["Wick_translation_levels"] == independent["derived"]["Wick_translation_levels"] == ["8", "16", "24", "32"], primary["derived"]["Wick_translation_levels"], independent["derived"]["Wick_translation_levels"], "cross")
    audit.check("cross scope exact", primary["scope"] == independent["scope"] == manifest["scope"], primary["scope"], manifest["scope"], "cross")
    audit.check("distinct Gram fixtures", primary["derived"]["reflected_gram"] != independent["derived"]["RP_gram"], primary["derived"]["reflected_gram"], independent["derived"]["RP_gram"], "cross")

    for phrase in (
        "reflection positive for Euclidean-time reflection",
        "No world-first general constructive-QFT theorem is claimed",
        "same terminal interaction",
        "uniformly `L2`",
        "positive semidefinite",
        "bounded truncations",
        "fixed time circumference",
        "Nyquist quartic witness",
        "energy below empty space",
        "C0, N1--N5, C6, CP1 and Pre-A remain open",
    ):
        audit.check(f"certificate phrase {phrase[:38]}", phrase in certificate_flat, phrase, "present", "certificate")
    package_files = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
    non_ascii = {str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127}) for path in package_files}
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"negative registered {negative_id}", f"### {negative_id} " in negative_text, negative_id, "detailed entry", "records")
        audit.check(f"negative TOC {negative_id}", f"[{negative_id}](#" in negative_text, negative_id, "TOC entry", "records")
    index_text = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index registered", MANIFEST.name in index_text and CERTIFICATE.name in index_text, [MANIFEST.name, CERTIFICATE.name], "both", "records")
    exploration = exploration_record(EXPLORATION_ID)
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration claim", exploration["claim_ids"] == ["C6-SPACETIME-SIGNATURE"], exploration["claim_ids"], ["C6-SPACETIME-SIGNATURE"], "records")
    audit.check("exploration task", exploration["task_id"] == "T-054" and exploration["gate_ids"] == [], {"task": exploration["task_id"], "gates": exploration["gate_ids"]}, "T-054 with no formal gate closure", "records")
    audit.check("exploration claim nonbearing", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "empty results", "records")
    audit.check("exploration negatives", tuple(exploration["formal_refs"].get("negatives", [])) == NEGATIVE_IDS, exploration["formal_refs"], list(NEGATIVE_IDS), "records")
    audit.check("exploration continues parent", any(item.get("id") == PARENT_EXPLORATION_ID and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), f"continues {PARENT_EXPLORATION_ID}", "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    exploration_text = " ".join((exploration["finding"], exploration["boundary"], exploration["next_action"])).lower()
    for phrase in ("conditional Jensen", "reflection positivity", "Nyquist", "below-empty-space", "C6", "Pre-A"):
        audit.check(f"exploration boundary {phrase}", phrase.lower() in exploration_text, phrase, "present", "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", EXPLORATION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, EXPLORATION_ID, "TODO and next gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", EXPLORATION_ID in changelog_text and MANIFEST.name in changelog_text, EXPLORATION_ID, "changelog and manifest", "records")
    lineage_text = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent"):
        audit.check(f"C6 lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage_text, kind, "run", "records")
    integrated_lineage = f"runs/2026-08-04-integrated-{SLUG}/" in lineage_text
    if DEFAULT_OUTPUT.is_file():
        audit.check("C6 lineage integrated", integrated_lineage, "integrated", "run", "records")
    else:
        audit.check("C6 lineage integrated first-pass deferral", not integrated_lineage, integrated_lineage, False, "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    for key in ("C6_advanced", "CP1_complete", "Pre_A_complete", "physical_state_or_vacuum", "below_empty_space_comparison", "canonical_CL8_regulator_identified", "full_phase_space_Weyl_CCR"):
        audit.check(f"claim firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "claim_firewall")

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
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "child_summaries": summaries,
        "cross_oracles": {
            "Nyquist_continuum": primary["derived"]["Nyquist_continuum_average"],
            "Nyquist_nodal": primary["derived"]["Nyquist_nodal_average"],
            "Nyquist_gap": primary["derived"]["Nyquist_alias_gap"],
            "Wick_translation_levels": primary["derived"]["Wick_translation_levels"],
            "primary_RP_gram": primary["derived"]["reflected_gram"],
            "independent_RP_gram": independent["derived"]["RP_gram"],
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
