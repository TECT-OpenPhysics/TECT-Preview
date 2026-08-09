#!/usr/bin/env python3
"""Integrated repository verifier for EXP-000781."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-EUCLIDEAN-DLR-TANGENT-STATE-AND-PHASE-BOUNDARY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY"
EXPLORATION_ID = "EXP-000781"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-Q3-PHASE-SIGN-AND-KMS-SPLIT"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


def portable_sha256(path: Path) -> str:
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
        timeout=120,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-exp774-") as temporary:
        temp = Path(temporary)
        primary_fresh, primary_stdout = run_fresh(PRIMARY, temp / "primary.json")
        independent_fresh, independent_stdout = run_fresh(INDEPENDENT, temp / "independent.json")

    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))

    for label, payload in (("primary fresh", primary_fresh), ("independent fresh", independent_fresh), ("primary stored", primary_stored), ("independent stored", independent_stored)):
        audit.check(f"{label} verdict", payload["verdict"] == "PASS", payload["verdict"], "PASS", "implementations")
        audit.check(f"{label} all assertions", payload["assertions"]["passed"] == payload["assertions"]["total"], payload["assertions"], "all pass", "implementations")
        audit.check(f"{label} candidate", payload["candidate_id"] == CANDIDATE_ID, payload["candidate_id"], CANDIDATE_ID, "implementations")
        audit.check(f"{label} result", payload["result_id"] == RESULT_ID, payload["result_id"], RESULT_ID, "implementations")
        audit.check(f"{label} exploration", payload["exploration_id"] == EXPLORATION_ID, payload["exploration_id"], EXPLORATION_ID, "implementations")
        audit.check(f"{label} next gate", payload["next_gate"] == NEXT_GATE, payload["next_gate"], NEXT_GATE, "implementations")
        audit.check(f"{label} claim nonbearing", payload["claim_bearing"] is False, payload["claim_bearing"], False, "implementations")

    audit.check("fresh primary stdout", "PRIMARY PASS" in primary_stdout, primary_stdout, "PRIMARY PASS", "implementations")
    audit.check("fresh independent stdout", "INDEPENDENT PASS" in independent_stdout, independent_stdout, "INDEPENDENT PASS", "implementations")
    audit.check("stored/fresh primary total", primary_stored["assertions"]["total"] == primary_fresh["assertions"]["total"], primary_stored["assertions"]["total"], primary_fresh["assertions"]["total"], "implementations")
    audit.check("stored/fresh independent total", independent_stored["assertions"]["total"] == independent_fresh["assertions"]["total"], independent_stored["assertions"]["total"], independent_fresh["assertions"]["total"], "implementations")
    audit.check("cross scope", primary_fresh["scope"] == independent_fresh["scope"] == manifest["scope"], [primary_fresh["scope"], independent_fresh["scope"]], manifest["scope"], "implementations")
    audit.check("cross Q3 spectrum", primary_fresh["derived"]["q3_laplacian_spectrum"] == {"0": 1, "2": 3, "4": 3, "6": 1}, primary_fresh["derived"]["q3_laplacian_spectrum"], {"0": 1, "2": 3, "4": 3, "6": 1}, "implementations")
    audit.check("independent Q3 spectrum", independent_fresh["derived"]["q3_spectrum"] == [0, 2, 2, 2, 4, 4, 4, 6], independent_fresh["derived"]["q3_spectrum"], [0, 2, 2, 2, 4, 4, 4, 6], "implementations")
    audit.check("primary tangent DLR true", primary_fresh["scope"]["source_tangent_zero_source_DLR_states"] is True, primary_fresh["scope"]["source_tangent_zero_source_DLR_states"], True, "scope")
    audit.check("positive lambda cusp false", primary_fresh["scope"]["positive_lambda_pressure_cusp"] is False, primary_fresh["scope"]["positive_lambda_pressure_cusp"], False, "scope")
    audit.check("KMS false", primary_fresh["scope"]["algebraic_KMS_for_preexisting_dynamics"] is False, primary_fresh["scope"]["algebraic_KMS_for_preexisting_dynamics"], False, "scope")
    audit.check("Pre-A false", primary_fresh["scope"]["Pre_A_complete"] is False, primary_fresh["scope"]["Pre_A_complete"], False, "scope")

    expected_paths = [MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, Path(__file__).resolve(), PRIMARY_STORED, INDEPENDENT_STORED]
    for path in expected_paths:
        audit.check(f"file exists {path.name}", path.is_file(), path, "file", "files")
        audit.check(f"file nonempty {path.name}", path.stat().st_size > 100, path.stat().st_size, ">100", "files")
    audit.check("manifest hash primary", primary_stored["files"]["manifest_sha256"] == portable_sha256(MANIFEST), primary_stored["files"]["manifest_sha256"], portable_sha256(MANIFEST), "files")
    audit.check("manifest hash independent", independent_stored["files"]["manifest_sha256"] == portable_sha256(MANIFEST), independent_stored["files"]["manifest_sha256"], portable_sha256(MANIFEST), "files")
    audit.check("certificate hash primary", primary_stored["files"]["certificate_sha256"] == portable_sha256(CERTIFICATE), primary_stored["files"]["certificate_sha256"], portable_sha256(CERTIFICATE), "files")
    audit.check("certificate hash independent", independent_stored["files"]["certificate_sha256"] == portable_sha256(CERTIFICATE), independent_stored["files"]["certificate_sha256"], portable_sha256(CERTIFICATE), "files")

    explorations = jsonl_records(REPO / "explorations/log.jsonl")
    exploration_matches = [record for record in explorations if record.get("id") == EXPLORATION_ID]
    audit.check("one exploration record", len(exploration_matches) == 1, len(exploration_matches), 1, "records")
    exploration = exploration_matches[0]
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration result evidence", any(RESULT_ID in item for item in exploration.get("evidence_refs", [])) or RESULT_ID in exploration.get("finding", ""), exploration.get("finding"), RESULT_ID, "records")
    audit.check("exploration next gate", NEXT_GATE in exploration["next_action"], exploration["next_action"], NEXT_GATE, "records")

    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    prior_art = (REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md").read_text(encoding="utf-8")
    negative_registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    todo = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    changelog = jsonl_records(REPO / "changelog/log.jsonl")
    catalog_md = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    catalog_json = json.loads((REPO / "verification/catalog.json").read_text(encoding="utf-8"))
    proof_map_md = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    proof_map_json_text = (REPO / "verification/proof-evidence-map.json").read_text(encoding="utf-8")
    claims_md = (REPO / "CLAIMS.md").read_text(encoding="utf-8")

    audit.check("gate parent present", PARENT_GATE in gates, PARENT_GATE in gates, True, "records")
    audit.check("gate partial status", "EXP-000781" in gates and "PARTIALLY RESOLVED" in gates, "EXP-000781" in gates, True, "records")
    audit.check("successor gate present", NEXT_GATE in gates, NEXT_GATE in gates, True, "records")
    audit.check("strategy index package", f"{SLUG}-manifest.json" in strategy_index, f"{SLUG}-manifest.json" in strategy_index, True, "records")
    audit.check("strategy index result", RESULT_ID in strategy_index, RESULT_ID in strategy_index, True, "records")
    audit.check("prior-art EXP774", EXPLORATION_ID in prior_art, EXPLORATION_ID in prior_art, True, "records")
    audit.check("prior-art DLR scope", "source-tangent" in prior_art and "positive-`lambda`" in prior_art, "source-tangent" in prior_art, True, "records")
    for negative_id in manifest["reused_negative_ids"]:
        audit.check(f"reused negative {negative_id}", negative_id in negative_registry, negative_id in negative_registry, True, "records")

    tasks = todo.get("tasks", todo if isinstance(todo, list) else [])
    task_matches = [task for task in tasks if task.get("id") == "T-054"]
    audit.check("T-054 unique", len(task_matches) == 1, len(task_matches), 1, "records")
    task = task_matches[0]
    audit.check("T-054 in progress", task["status"] == "in_progress", task["status"], "in_progress", "records")
    audit.check("T-054 successor gate history", NEXT_GATE in task["note"], task["note"], NEXT_GATE, "records")
    audit.check("T-054 EXP774 note", EXPLORATION_ID in task["note"], task["note"], EXPLORATION_ID, "records")

    changelog_matches = [entry for entry in changelog if EXPLORATION_ID.lower() in entry.get("header", "").lower()]
    audit.check("changelog EXP774 unique", len(changelog_matches) == 1, len(changelog_matches), 1, "records")
    audit.check("changelog manifest", f"strategy/{SLUG}-manifest.json" in changelog_matches[0]["notes"], changelog_matches[0]["notes"], f"strategy/{SLUG}-manifest.json", "records")

    for relative in (
        f"strategy/{SLUG}-manifest.json",
        f"strategy/{SLUG}-certificate-260804.md",
        f"codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split.py",
        f"codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split_independent.py",
        f"codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split_verify.py",
    ):
        audit.check(f"catalog markdown {relative}", relative in catalog_md, relative in catalog_md, True, "generated")
        audit.check(f"catalog json {relative}", relative in json.dumps(catalog_json), relative in json.dumps(catalog_json), True, "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map_md and EXPLORATION_ID in proof_map_json_text, [EXPLORATION_ID in proof_map_md, EXPLORATION_ID in proof_map_json_text], [True, True], "generated")
    audit.check("proof map result", RESULT_ID in proof_map_md and RESULT_ID in proof_map_json_text, [RESULT_ID in proof_map_md, RESULT_ID in proof_map_json_text], [True, True], "generated")
    audit.check("proof map successor", NEXT_GATE in proof_map_md and NEXT_GATE in proof_map_json_text, [NEXT_GATE in proof_map_md, NEXT_GATE in proof_map_json_text], [True, True], "generated")
    audit.check("CLAIMS count C6 once", claims_md.count("C6-SPACETIME-SIGNATURE") >= 1, claims_md.count("C6-SPACETIME-SIGNATURE"), ">=1", "generated")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    payload = {
        "schema": f"tect/{SLUG}-integrated/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
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
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000781 INTEGRATED PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
