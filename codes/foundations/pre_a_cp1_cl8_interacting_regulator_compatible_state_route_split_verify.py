#!/usr/bin/env python3
"""Integrated verifier for the interacting regulator-compatible state route split."""

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
SLUG = "pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-STATE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-LOW-MODE-GROUND-ENTANGLEMENT-ALL-BETA-PROJECTIVITY-AND-Q3-WICK-COUNTERTERM-OBSTRUCTIONS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION",
)
EXPLORATION_ID = "EXP-000764"
PARENT_IDS = (
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-manifest.json",
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
    with tempfile.TemporaryDirectory(prefix="tect-prea-interacting-state-") as directory:
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
        audit.check(f"{name} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "child")
        audit.check(f"{name} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "freshness")
        for parent_file in PARENT_FILES:
            audit.check(f"{name} parent hash {Path(parent_file).name}", child["source_sha256"][parent_file] == sha256(REPO / parent_file), child["source_sha256"][parent_file], sha256(REPO / parent_file), "freshness")
        audit.check(f"{name} assertions", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "child")
        audit.check(f"{name} command summary", summaries[name] == child["assertion_summary"], summaries[name], child["assertion_summary"], "child")

    audit.check("mixed derivative cross agreement", primary["derived"]["collective_fixture"]["mixed_derivative"] == independent["derived"]["collective_fixture"]["mixed_derivative"], primary["derived"]["collective_fixture"], independent["derived"]["collective_fixture"], "cross")
    audit.check("mixed derivative oracle", primary["derived"]["collective_fixture"]["mixed_derivative"] == "3/2", primary["derived"]["collective_fixture"], "3/2", "oracle")
    audit.check("Q3 spectrum cross agreement", primary["derived"]["Q3_spectrum"] == independent["derived"]["Q3_spectrum"], primary["derived"]["Q3_spectrum"], independent["derived"]["Q3_spectrum"], "cross")
    audit.check("Wick fixture cross agreement", primary["derived"]["Wick_fixture"] == independent["derived"]["Wick_fixture"], primary["derived"]["Wick_fixture"], independent["derived"]["Wick_fixture"], "cross")
    primary_covariance = primary["derived"]["covariance_values"]
    independent_covariance = independent["derived"]["covariance_values"]
    audit.check("covariance sequence cross agreement", len(primary_covariance) == len(independent_covariance) and all(abs(a - b) < 1e-14 for a, b in zip(primary_covariance, independent_covariance)), primary_covariance, independent_covariance, "cross")

    for child_name, child in (("primary", primary), ("independent", independent)):
        names = {row["name"] for row in child["assertions"]}
        required = (
            "collective plane" if child_name == "primary" else "collective plane fixture",
            "mixed derivative",
            "marginal",
            "Gibbs",
            "mean-force",
            "edge Wick",
            "Q3 spectrum",
            "Wick Walsh shift" if child_name == "primary" else "Wick shift",
            "covariance",
            "scope false: Pre_A_complete",
        )
        for fragment in required:
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
        "section-3-natural-low-high-split",
        "section-4-purity-factorization-lemma",
        "section-5-collective-uniform-nyquist-witness",
        "section-6-ground-projectivity-no-go",
        "section-7-gibbs-and-mean-force",
        "section-8-history-cut-consequence",
        "section-9-common-diagonal-wick-calculus",
        "section-10-q3-counterterm-matrix",
        "section-11-logarithmic-reference-growth",
        "section-12-open-positive-route",
        "section-14-adversarial-review",
        "section-16-next-gate",
    )
    for anchor in anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate, anchor, "present", "certificate")
    audit.check("entanglement formula certificate", "partial_X^2\\partial_Y^2U_N={6g\\over L}>0" in certificate, "present", "6g/L", "certificate")
    audit.check("mean-force formula certificate", "H_{N\\to M}^{\\rm mf}(\\beta)" in certificate and "-\\beta^{-1}\\log A_\\beta" in certificate, "present", "mean force", "certificate")
    audit.check("Wick matrix certificate", "-3C[(g+\\lambda)I+\\lambda L_{Q3}]" in certificate, "present", "Q3 matrix", "certificate")
    audit.check("isolated beta firewall", "does not exclude one isolated finite `beta`" in certificate_flat, "present", "isolated beta open", "certificate")
    audit.check("counterterm sufficiency firewall", "not a proof that the enlarged theory converges" in certificate_flat, "present", "convergence open", "certificate")
    audit.check("physical reference firewall", "does not identify physical empty space" in certificate_flat, "present", "physical reference open", "certificate")
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
    audit.check("exploration continues prior route", any(item.get("id") == "EXP-000762" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000762", "records")
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
            "mixed_derivative_fixture": primary["derived"]["collective_fixture"]["mixed_derivative"],
            "Q3_spectrum": primary["derived"]["Q3_spectrum"],
            "Wick_fixture": primary["derived"]["Wick_fixture"],
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
