#!/usr/bin/env python3
"""Integrated verifier for the centered Q3 Wick/Weyl limit route split."""

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
SLUG = "pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CENTERED-Q3-WICK-WEYL-LIMIT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-UNIT-FREE-RP-WEYL-SEAM-AND-CENTERED-Q3-WICK-LP-LIMIT-WITH-UI-GATES"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT",
    "NG-2026-08-04-PRE-A-CP1-CL8-WICK-L2-ONLY-INTERACTING-DENSITY-LIMIT",
)
EXPLORATION_ID = "EXP-000770"
PARENT_EXPLORATION_ID = "EXP-000769"
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

    with tempfile.TemporaryDirectory(prefix="tect-centered-q3-weyl-integrated-") as temporary:
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
    for name in (
        "unit time derivative coefficient",
        "unit onsite quartic coefficient",
        "fixed mode O(a^2) stable ratio",
        "common coupling Hminus error decreases 48 to 96",
        "low-band M>4K exact degree 4",
        "chaos alias tail decreases",
        "Q3 Laplacian Walsh spectrum",
        "tuned raw recovers fixed KR C=11",
        "centered reflected Gram PSD (1.0, -2.0, 1.0)",
        "Weyl product cocycle sign",
        "Weyl seam midpoint phase",
        "free Weyl O(a^2) ratio",
        "rare spike exponential contribution grows",
        "scope firewall below_empty_space_comparison",
    ):
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in (
        "independent unit time coefficient",
        "independent unit quartic coefficient",
        "independent fixed symbol second order",
        "independent low-band exact degree 4",
        "independent convolution alias tail",
        "independent Q3 edge Wick contraction",
        "independent tuned counterterm C=15",
        "independent RP Gram symmetric",
        "independent Weyl cocycle sign",
        "independent Weyl complex phase",
        "independent free Weyl second order",
        "independent rare spike exponential",
        "independent scope firewall below_empty_space_comparison",
    ):
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    direct, from_modules, dynamic = imported_modules(INDEPENDENT)
    audit.check("independent AST primary firewall", PRIMARY.stem not in direct and PRIMARY.stem not in from_modules, sorted(direct | from_modules), f"not {PRIMARY.stem}", "independence")
    audit.check("independent AST numeric firewall", not ({"sympy", "numpy", "scipy"} & (direct | from_modules)), sorted(direct | from_modules), "stdlib only", "independence")
    audit.check("independent AST dynamic firewall", not dynamic and "runpy" not in direct and "importlib" not in direct, {"dynamic": sorted(dynamic), "imports": sorted(direct)}, "none", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    audit.check("cross low-band exact", all(values == [0] for values in primary["derived"]["low_aliases"].values()) and all(values == [0] for values in independent["derived"]["low_aliases"].values()), {"primary": primary["derived"]["low_aliases"], "independent": independent["derived"]["low_aliases"]}, "only zero sector", "cross")
    audit.check("cross full quartic aliases", any(value != 0 for value in primary["derived"]["full_aliases"]["4"]) and any(value != 0 for value in independent["derived"]["full_aliases"]["4"]), {"primary": primary["derived"]["full_aliases"]["4"], "independent": independent["derived"]["full_aliases"]["4"]}, "nonzero aliases", "cross")
    audit.check("cross convolution tails decrease", all(rows[2] < rows[1] < rows[0] for rows in (primary["derived"]["convolution_tails"], independent["derived"]["convolution_tails"])), {"primary": primary["derived"]["convolution_tails"], "independent": independent["derived"]["convolution_tails"]}, "both decrease", "cross")
    audit.check("cross Q3 four levels", len(primary["derived"]["Q3_counterterm_levels"]) == len(independent["derived"]["Q3_counterterm_levels"]) == 4, {"primary": primary["derived"]["Q3_counterterm_levels"], "independent": independent["derived"]["Q3_counterterm_levels"]}, "four", "cross")
    audit.check("cross free Weyl errors decrease", all(rows[2] < rows[1] < rows[0] for rows in (primary["derived"]["Weyl_characteristic_errors"], independent["derived"]["Weyl_characteristic_errors"])), {"primary": primary["derived"]["Weyl_characteristic_errors"], "independent": independent["derived"]["Weyl_characteristic_errors"]}, "both decrease", "cross")
    audit.check("distinct RP fixtures", primary["derived"]["reflected_gram"] != independent["derived"]["RP_gram"], primary["derived"]["reflected_gram"], independent["derived"]["RP_gram"], "cross")
    audit.check("cross scope exact", primary["scope"] == independent["scope"] == manifest["scope"], primary["scope"], manifest["scope"], "cross")

    for phrase in (
        "not a world-first or novelty proof",
        "full-sequence centered free limit",
        "Riemann--Lebesgue lemma",
        "Fixed-raw no-go",
        "uniform exponential moment",
        "twisted-Weyl heat-kernel seam identity",
        "off-diagonal seam",
        "energy below empty space",
        "C0, N1--N5, C6, CP1, Sector A, and Pre-A",
    ):
        audit.check(f"certificate phrase {phrase[:38]}", phrase.lower() in certificate_flat.lower(), phrase, "present", "certificate")
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
    exploration_text = " ".join((exploration["finding"], exploration["boundary"], exploration["next_action"]))
    for phrase in ("unit dictionary", "finite-Lp", "counterterm", "Weyl seam", "below-empty-space", "C6", "Pre-A"):
        audit.check(f"exploration boundary {phrase}", phrase.lower() in exploration_text.lower(), phrase, "present", "records")
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
    for key in ("fixed_raw_CL8_finite_Q3_renormalized_limit", "centered_Q3_uniform_exponential_integrability", "centered_Q3_interacting_density_L1_limit", "interacting_full_phase_space_Weyl_CCR", "physical_state_or_vacuum", "below_empty_space_comparison", "C6_advanced", "CP1_complete", "Pre_A_complete"):
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
            "primary_aliases": primary["derived"]["full_aliases"],
            "independent_aliases": independent["derived"]["full_aliases"],
            "primary_counterterm_levels": primary["derived"]["Q3_counterterm_levels"],
            "independent_counterterm_levels": independent["derived"]["Q3_counterterm_levels"],
            "primary_Weyl_errors": primary["derived"]["Weyl_characteristic_errors"],
            "independent_Weyl_errors": independent["derived"]["Weyl_characteristic_errors"],
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
