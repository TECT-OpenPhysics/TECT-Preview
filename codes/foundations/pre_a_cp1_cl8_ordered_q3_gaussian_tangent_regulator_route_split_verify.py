#!/usr/bin/env python3
"""Integrated verifier for the ordered-Q3 Gaussian tangent regulator split."""

from __future__ import annotations

import argparse
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
SLUG = "pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split"
CANDIDATE_ID = "PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-SPECTRAL-GAUSSIAN-PROJECTIVE-FAMILY-HADAMARD-COMPARATOR-BARE-CRITICAL-SPEED-CENTERED-PROJECTIVITY-AND-CRITICAL-ZERO-MODE-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND",
)
EXPLORATION_ID = "EXP-000762"
PARENT_IDS = (
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json",
    "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
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
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-prea-q3gauss-") as directory:
        root = Path(directory)
        primary, primary_stdout = run_child(PRIMARY, root / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, root / "independent.json")
    command_summaries = {
        "primary": child_summary(primary_stdout),
        "independent": child_summary(independent_stdout),
    }

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
        audit.check(f"{name} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "child")
        audit.check(f"{name} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "freshness")
        for parent_file in PARENT_FILES:
            audit.check(f"{name} parent hash {Path(parent_file).name}", child["source_sha256"][parent_file] == sha256(REPO / parent_file), child["source_sha256"][parent_file], sha256(REPO / parent_file), "freshness")
        audit.check(f"{name} assertions pass", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "child")
        audit.check(f"{name} command summary", command_summaries[name] == child["assertion_summary"], command_summaries[name], child["assertion_summary"], "child")

    audit.check("Q3 spectrum cross agreement", primary["derived"]["Q3_spectrum"] == independent["derived"]["Q3_spectrum"], primary["derived"]["Q3_spectrum"], independent["derived"]["Q3_spectrum"], "cross")
    audit.check("ordered fixture cross agreement", primary["derived"]["ordered_fixture"] == independent["derived"]["ordered_fixture"], primary["derived"]["ordered_fixture"], independent["derived"]["ordered_fixture"], "cross")
    audit.check("centered fixture cross agreement", primary["derived"]["centered_fixture"] == independent["derived"]["centered_fixture"], primary["derived"]["centered_fixture"], independent["derived"]["centered_fixture"], "cross")
    audit.check("bare critical cross agreement", primary["derived"]["bare_critical"] == independent["derived"]["bare_critical"], primary["derived"]["bare_critical"], independent["derived"]["bare_critical"], "cross")
    audit.check("coarse symbol oracle", primary["derived"]["centered_fixture"]["coarse_symbol_squared"] == "3", primary["derived"]["centered_fixture"], "3", "oracle")
    audit.check("fine symbol oracle", primary["derived"]["centered_fixture"]["fine_symbol_squared"] == "4", primary["derived"]["centered_fixture"], "4", "oracle")
    audit.check("Q3 multiplicity oracle", primary["derived"]["Q3_spectrum"]["multiplicities"] == [1, 3, 3, 1], primary["derived"]["Q3_spectrum"], [1, 3, 3, 1], "oracle")

    for child_name, child in (("primary", primary), ("independent", independent)):
        names = {row["name"] for row in child["assertions"]}
        required_fragments = (
            "Walsh eigenvector",
            "ordered fixture",
            "canonical",
            "spectral restriction" if child_name == "independent" else "spectral projective restriction",
            "coarse fixture" if child_name == "independent" else "coarse symbol fixture",
            "fine fixture" if child_name == "independent" else "fine symbol fixture",
            "centered series" if child_name == "independent" else "centered symbol series",
            "lambda-zero",
            "global centered symbol bound" if child_name == "primary" else "derived nu half",
            "finite-time",
            "z one" if child_name == "independent" else "gap times correlation",
            "zero covariance",
            "Hadamard",
            "effective metric",
            "scope false: Pre_A_complete",
        )
        for fragment in required_fragments:
            audit.check(f"{child_name} coverage {fragment}", any(fragment in name for name in names), fragment, "present", "coverage")
    independent_source = INDEPENDENT.read_text(encoding="utf-8").lower()
    audit.check("independent has no SymPy", "import sympy" not in independent_source, "absent", "absent", "independence")
    audit.check("independent has no NumPy", "import numpy" not in independent_source, "absent", "absent", "independence")
    audit.check("independent does not import primary", SLUG.replace("-", "_") not in independent_source.replace(SLUG.replace("-", "_") + "_independent", ""), "absent", "absent", "independence")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    audit.check("stored primary fresh", PRIMARY_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(primary), sha256(PRIMARY_STORED), hashlib.sha256(canonical_bytes(primary)).hexdigest(), "stored")
    audit.check("stored independent fresh", INDEPENDENT_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(independent), sha256(INDEPENDENT_STORED), hashlib.sha256(canonical_bytes(independent)).hexdigest(), "stored")

    anchors = (
        "section-4-exact-q3-ordered-hessian",
        "section-5-canonical-mode-normalization",
        "section-6-spectral-projective-state-theorem",
        "section-7-hadamard-comparator",
        "section-8-centered-fixed-mode-limit",
        "section-9-centered-projectivity-no-go",
        "section-10-bare-critical-scaling-and-speed",
        "section-11-critical-zero-mode-no-go",
        "section-12-history-cut-composition-boundary",
        "section-14-adversarial-review",
        "section-16-next-gate",
    )
    for anchor in anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate, anchor, "present", "certificate")
    audit.check("projective identity typed", "omega_(K_prime) composed with iota_(K,K_prime)=omega_K" in manifest["spectral_projective_state_family"]["projective_identity"], manifest["spectral_projective_state_family"]["projective_identity"], "typed state identity", "certificate")
    hadamard = manifest["Hadamard_comparator"]
    audit.check("effective metric manifest", "ds^2=-dt^2+(chi/c)dx^2" in hadamard["effective_geometry"], hadamard["effective_geometry"], "typed effective metric", "certificate")
    audit.check("field rescaling manifest", "phi=(chi*c)^(1/4)*Phi" in hadamard["effective_geometry"] and "mass_s^2=nu_s/chi" in hadamard["effective_geometry"], hadamard["effective_geometry"], "typed field and mass map", "certificate")
    audit.check("full Cauchy extension manifest", "extend continuously" in hadamard["full_Cauchy_extension"], hadamard["full_Cauchy_extension"], "continuous smooth-data extension", "certificate")
    audit.check("spacetime distribution manifest", "as a distribution" in hadamard["spacetime_two_point"], hadamard["spacetime_two_point"], "distribution", "certificate")
    audit.check("exact cutoff restriction manifest", "exact finite-mode restriction" in hadamard["spacetime_two_point"], hadamard["spacetime_two_point"], "exact restriction", "certificate")
    audit.check("frequency not covariance certificate", "positive **frequency operator**" in certificate and "It is not itself a covariance" in certificate, "present", "typed operator distinction", "certificate")
    audit.check("Cauchy covariance block certificate", "equal-time symmetrized Cauchy covariance block" in certificate and "\\Gamma=" in certificate, "present", "Gamma block", "certificate")
    audit.check("spacetime two-point certificate", "W_\\alpha(t,x;t',x')" in certificate and "Every finite-mode restriction" in certificate, "present", "distribution and restrictions", "certificate")
    audit.check("effective geometry certificate", "ds^2=-dt^2+{\\chi\\over c}" in certificate and "\\phi_\\alpha=(\\chi c)^{1/4}\\Phi_\\alpha" in certificate, "present", "metric and field rescaling", "certificate")
    audit.check("Hadamard DOI present", "10.1016/0003-4916(81)90098-1" in certificate, "present", "DOI", "certificate")
    audit.check("zero-mode source present", "2108.07274" in certificate, "present", "arXiv source", "certificate")
    audit.check("physical light firewall", "It does not derive physical light" in certificate, "present", "not derived", "certificate")
    audit.check("phase transition firewall", "not a proof of a thermodynamic" in certificate, "present", "not proved", "certificate")
    audit.check("interacting limit firewall", "do not disappear merely because" in certificate, "present", "interactions remain", "certificate")
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
    audit.check("exploration result refs empty", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "claim-nonbearing", "records")
    audit.check("exploration negatives", tuple(exploration["formal_refs"].get("negatives", [])) == NEGATIVE_IDS, exploration["formal_refs"], list(NEGATIVE_IDS), "records")
    audit.check("exploration continues quantum route", any(item.get("id") == "EXP-000761" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000761", "records")
    audit.check("exploration continues critical seed", any(item.get("id") == "EXP-000623" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000623", "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", EXPLORATION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, EXPLORATION_ID, "TODO plus next gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", EXPLORATION_ID in changelog_text and MANIFEST.name in changelog_text, EXPLORATION_ID, "changelog plus manifest", "records")
    lineage_text = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    audit.check("C6 lineage primary run", f"runs/2026-08-04-primary-{SLUG}/" in lineage_text, SLUG, "primary run", "records")
    audit.check("C6 lineage independent run", f"runs/2026-08-04-independent-{SLUG}/" in lineage_text, SLUG, "independent run", "records")
    audit.check("C6 lineage integrated run", f"runs/2026-08-04-integrated-{SLUG}/" in lineage_text, SLUG, "integrated run", "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("C6 advancement false", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "claim_firewall")
    audit.check("Pre-A false", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "claim_firewall")

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
        "status": manifest["status"],
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
        },
        "child_assertions": {"primary": primary["assertion_summary"], "independent": independent["assertion_summary"]},
        "shared_invariants": {
            "Q3_spectrum": primary["derived"]["Q3_spectrum"],
            "ordered_fixture": primary["derived"]["ordered_fixture"],
            "centered_fixture": primary["derived"]["centered_fixture"],
            "bare_critical": primary["derived"]["bare_critical"],
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "total_assertions": len(audit.rows) + primary["assertion_summary"]["total"] + independent["assertion_summary"]["total"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-stored", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.check_stored:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != payload:
            raise AssertionError("stored integrated result differs from fresh payload")
        summary = payload["assertion_summary"]
        print(f"PASS {summary['passed']}/{summary['total']} stored integrated; {payload['total_assertions']} total")
        return 0
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"PASS {summary['passed']}/{summary['total']} integrated; {payload['total_assertions']} total -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
