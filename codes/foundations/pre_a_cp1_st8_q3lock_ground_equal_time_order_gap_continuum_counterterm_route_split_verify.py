#!/usr/bin/env python3
"""Integrated repository verifier for EXP-000789."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION"
EXPLORATION_ID = "EXP-000789"
PRIMARY_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-G-LAMBDA-ONLY-4D-ONE-LOOP-CLOSURE",
)
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-integrated-{SLUG}/result.json"


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def run_fresh(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def jsonl_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-exp789-") as temporary:
        temp = Path(temporary)
        primary_fresh, primary_stdout = run_fresh(PRIMARY, temp / "primary.json")
        independent_fresh, independent_stdout = run_fresh(INDEPENDENT, temp / "independent.json")

    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    payloads = (
        ("primary fresh", primary_fresh),
        ("independent fresh", independent_fresh),
        ("primary stored", primary_stored),
        ("independent stored", independent_stored),
    )
    for label, payload in payloads:
        audit.check(f"{label} verdict", payload["verdict"] == "PASS", payload["verdict"], "PASS", "implementations")
        assertion_summary = {key: payload["assertions"][key] for key in ("passed", "total")}
        audit.check(f"{label} assertions", assertion_summary["passed"] == assertion_summary["total"], assertion_summary, "all pass", "implementations")
        audit.check(f"{label} candidate", payload["candidate_id"] == CANDIDATE_ID, payload["candidate_id"], CANDIDATE_ID, "implementations")
        audit.check(f"{label} result", payload["result_id"] == RESULT_ID, payload["result_id"], RESULT_ID, "implementations")
        audit.check(f"{label} exploration", payload["exploration_id"] == EXPLORATION_ID, payload["exploration_id"], EXPLORATION_ID, "implementations")
        audit.check(f"{label} parent gate", payload["parent_gate"] == PARENT_GATE, payload["parent_gate"], PARENT_GATE, "implementations")
        audit.check(f"{label} negative ids", tuple(payload["negative_ids"]) == NEGATIVE_IDS, payload["negative_ids"], NEGATIVE_IDS, "implementations")
        audit.check(f"{label} nonbearing", payload["claim_bearing"] is False, payload["claim_bearing"], False, "implementations")

    audit.check("fresh primary stdout", "PRIMARY PASS" in primary_stdout, primary_stdout, "PRIMARY PASS", "implementations")
    audit.check("fresh independent stdout", "INDEPENDENT PASS" in independent_stdout, independent_stdout, "INDEPENDENT PASS", "implementations")
    audit.check("stored/fresh primary total", primary_stored["assertions"]["total"] == primary_fresh["assertions"]["total"], primary_stored["assertions"]["total"], primary_fresh["assertions"]["total"], "implementations")
    audit.check("stored/fresh independent total", independent_stored["assertions"]["total"] == independent_fresh["assertions"]["total"], independent_stored["assertions"]["total"], independent_fresh["assertions"]["total"], "implementations")
    audit.check("cross scope", primary_fresh["scope"] == independent_fresh["scope"] == manifest["scope"], [primary_fresh["scope"], independent_fresh["scope"]], manifest["scope"], "implementations")

    i3 = primary_fresh["derived"]["watson_I3"]
    j3 = primary_fresh["derived"]["half_watson_J3"]
    independent_last = independent_fresh["derived"]["finite_torus"][-1]
    audit.check("I3 canonical", math.isclose(i3, 0.505462019717326006, rel_tol=0.0, abs_tol=5e-15), i3, 0.505462019717326006, "constants")
    audit.check("J3 canonical", math.isclose(j3, 0.643953733381468096, rel_tol=0.0, abs_tol=5e-15), j3, 0.643953733381468096, "constants")
    audit.check("Cauchy margin", j3**2 < i3, j3**2, i3, "constants")
    audit.check("independent J3 diagnostic", abs(independent_last["J3_L"] - j3) < 2e-4, independent_last["J3_L"], j3, "constants")
    audit.check("primary d2 coefficient", primary_fresh["derived"]["one_loop_coefficients"]["distance_2"] == "4*lambda**2", primary_fresh["derived"]["one_loop_coefficients"]["distance_2"], "4*lambda**2", "counterterm")
    audit.check("independent d2 coefficient", independent_fresh["derived"]["one_loop_coefficients_gl_basis"]["distance_2"] == ["0", "0", "4"], independent_fresh["derived"]["one_loop_coefficients_gl_basis"]["distance_2"], ["0", "0", "4"], "counterterm")

    expected_paths = [MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, Path(__file__).resolve(), PRIMARY_STORED, INDEPENDENT_STORED]
    for path in expected_paths:
        audit.check(f"file exists {path.name}", path.is_file(), path, "file", "files")
        audit.check(f"file nonempty {path.name}", path.stat().st_size > 100, path.stat().st_size, ">100", "files")
    for label, stored in (("primary", primary_stored), ("independent", independent_stored)):
        audit.check(f"manifest hash {label}", stored["files"]["manifest_sha256"] == portable_sha256(MANIFEST), stored["files"]["manifest_sha256"], portable_sha256(MANIFEST), "files")
        audit.check(f"certificate hash {label}", stored["files"]["certificate_sha256"] == portable_sha256(CERTIFICATE), stored["files"]["certificate_sha256"], portable_sha256(CERTIFICATE), "files")

    explorations = jsonl_records(REPO / "explorations/log.jsonl")
    matches = [record for record in explorations if record.get("id") == EXPLORATION_ID]
    audit.check("one exploration", len(matches) == 1, len(matches), 1, "records")
    exploration = matches[0]
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration result", RESULT_ID in exploration["finding"], exploration["finding"], RESULT_ID, "records")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"exploration negative {negative_id}", negative_id in exploration["formal_refs"]["negatives"], exploration["formal_refs"], negative_id, "records")

    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    prior_art = (REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md").read_text(encoding="utf-8")
    negative_registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    todo = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    changelog = jsonl_records(REPO / "changelog/log.jsonl")
    catalog_md = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    catalog_json_text = (REPO / "verification/catalog.json").read_text(encoding="utf-8")
    proof_map_md = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    proof_map_json_text = (REPO / "verification/proof-evidence-map.json").read_text(encoding="utf-8")

    audit.check("parent gate present", PARENT_GATE in gates, PARENT_GATE in gates, True, "records")
    audit.check("parent partial EXP789", EXPLORATION_ID in gates and "PARTIALLY RESOLVED" in gates, EXPLORATION_ID in gates, True, "records")
    audit.check("physical reference retained", "physical empty space" in gates.lower() and "below-empty-space" in gates.lower(), "physical empty space" in gates.lower(), True, "records")
    audit.check("strategy manifest", f"{SLUG}-manifest.json" in strategy_index, f"{SLUG}-manifest.json" in strategy_index, True, "records")
    audit.check("strategy result", RESULT_ID in strategy_index, RESULT_ID in strategy_index, True, "records")
    audit.check("prior art EXP789", EXPLORATION_ID in prior_art, EXPLORATION_ID in prior_art, True, "records")
    audit.check("prior art no priority", "world-first" in prior_art and "No full-chain counterpart was located" in prior_art, "world-first" in prior_art, True, "records")
    for negative_id in (*NEGATIVE_IDS, *manifest["reused_negative_ids"]):
        audit.check(f"negative registry {negative_id}", negative_id in negative_registry, negative_id in negative_registry, True, "records")

    tasks = todo["tasks"]
    task_matches = [task for task in tasks if task.get("id") == "T-054"]
    audit.check("T-054 unique", len(task_matches) == 1, len(task_matches), 1, "records")
    task = task_matches[0]
    audit.check("T-054 in progress", task["status"] == "in_progress", task["status"], "in_progress", "records")
    audit.check("T-054 primary gate retained", task["gate"] == PRIMARY_GATE, task["gate"], PRIMARY_GATE, "records")
    audit.check("T-054 Q3LOCK parent gate retained", PARENT_GATE in task["note"], task["note"], PARENT_GATE, "records")
    audit.check("T-054 EXP789", EXPLORATION_ID in task["note"], task["note"], EXPLORATION_ID, "records")
    audit.check("T-054 empty firewall", "physical empty space" in task["note"].lower(), task["note"], "physical empty space", "records")

    changelog_matches = [entry for entry in changelog if EXPLORATION_ID.lower() in entry.get("header", "").lower() or EXPLORATION_ID.lower() in entry.get("raw", "").lower()]
    audit.check("changelog unique", len(changelog_matches) == 1, len(changelog_matches), 1, "records")
    audit.check("changelog manifest", f"strategy/{SLUG}-manifest.json" in changelog_matches[0]["notes"], changelog_matches[0]["notes"], f"strategy/{SLUG}-manifest.json", "records")

    relative_paths = (
        f"strategy/{SLUG}-manifest.json",
        f"strategy/{SLUG}-certificate-260809.md",
        "codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split.py",
        "codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split_independent.py",
        "codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split_verify.py",
    )
    for relative in relative_paths:
        audit.check(f"catalog markdown {relative}", relative in catalog_md, relative in catalog_md, True, "generated")
        audit.check(f"catalog json {relative}", relative in catalog_json_text, relative in catalog_json_text, True, "generated")
    for label, needle in (("exploration", EXPLORATION_ID), ("result", RESULT_ID), ("gate", PARENT_GATE), ("negative gap", NEGATIVE_IDS[0]), ("negative continuum", NEGATIVE_IDS[1])):
        audit.check(f"proof map {label}", needle in proof_map_md and needle in proof_map_json_text, [needle in proof_map_md, needle in proof_map_json_text], [True, True], "generated")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    return {
        "schema": f"tect/{SLUG}-integrated/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": PARENT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "component_assertions": {
            "primary": {"passed": primary_fresh["assertions"]["passed"], "total": primary_fresh["assertions"]["total"]},
            "independent": {"passed": independent_fresh["assertions"]["passed"], "total": independent_fresh["assertions"]["total"]},
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "primary_sha256": portable_sha256(PRIMARY),
            "independent_sha256": portable_sha256(INDEPENDENT),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000789 INTEGRATED PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
