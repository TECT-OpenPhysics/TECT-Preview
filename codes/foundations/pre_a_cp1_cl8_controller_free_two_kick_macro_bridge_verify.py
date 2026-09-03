#!/usr/bin/env python3
"""Integrated verifier for the controller-free CL8 two-kick macro bridge."""

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


__version__ = "0.2.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-controller-free-two-kick-macro-bridge"
CANDIDATE_ID = "PA-CP1-CL8-CONTROLLER-FREE-TWO-KICK-MACRO-BRIDGE-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-GLOBAL-SIDEWAYS-MACRO-AND-FIXED-REGULATOR-SPLITTING-BRIDGE"
ADMISSION_RESULT_ID = "PRE-A-ROUND1-PARTIAL-EVIDENCE-INTAKE-PINNED-M1-BARE-M5-SCOPED-FAILURES-AND-CURRENT-NONSELECTION"
NEGATIVE_IDS = [
    "NG-2026-08-09-PRE-A-CP1-CL8-RAW-PERIODIC-EO-RECTANGLE-QUOTIENT",
    "NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS",
]
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
ADMISSION = REPO / "strategy/pre-a-round1-admission-canonical-functional-bridge-manifest.json"
EVIDENCE = REPO / "strategy/pre-a-round1-boundary-evidence-register-260809-v0.1.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATION = REPO / "explorations/log.jsonl"
TODO = REPO / "todo/todo.json"
PROOF_MAP_MD = REPO / "theory/proof-evidence-map.md"
PROOF_MAP_JSON = REPO / "verification/proof-evidence-map.json"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-integrated-{SLUG}/result.json"


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


def canonical_cross_value(value: Any) -> Any:
    """Normalize mathematically identical column-vector JSON encodings."""
    if isinstance(value, dict):
        return {key: canonical_cross_value(item) for key, item in value.items()}
    if isinstance(value, list):
        if value and all(isinstance(item, list) and len(item) == 1 for item in value):
            return [canonical_cross_value(item[0]) for item in value]
        return [canonical_cross_value(item) for item in value]
    return value


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def run_child(script: Path, output: Path, profile: str) -> tuple[dict[str, Any], str]:
    command = [sys.executable, "-X", "utf8", str(script), "--profile", profile, "--output", str(output)]
    completed = subprocess.run(command, cwd=REPO, check=False, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"child failed: {command}\nstdout={completed.stdout}\nstderr={completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    stored_primary = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="tect-pre-a-macro-verify-") as temporary:
        temp = Path(temporary)
        fresh_primary, stdout_primary = run_child(PRIMARY, temp / "primary.json", "f0")
        fresh_independent, stdout_independent = run_child(INDEPENDENT, temp / "independent.json", "f0")

    audit.check("primary freshness", fresh_primary == stored_primary, sha256(PRIMARY_STORED), "fresh rerun exact", "freshness")
    audit.check("independent freshness", fresh_independent == stored_independent, sha256(INDEPENDENT_STORED), "fresh rerun exact", "freshness")
    primary_summary = stored_primary["assertion_summary"]
    independent_summary = stored_independent["assertion_summary"]
    primary_banner = f"{primary_summary['passed']}/{primary_summary['total']} PASS"
    independent_banner = f"{independent_summary['passed']}/{independent_summary['total']} PASS"
    audit.check("primary child stdout", primary_banner in stdout_primary, stdout_primary, primary_banner, "children")
    audit.check("independent child stdout", independent_banner in stdout_independent, stdout_independent, independent_banner, "children")
    audit.check("primary result id", stored_primary["result_id"] == RESULT_ID, stored_primary["result_id"], RESULT_ID, "children")
    audit.check("independent result id", stored_independent["result_id"] == RESULT_ID, stored_independent["result_id"], RESULT_ID, "children")
    audit.check("admission result agreement", stored_primary["admission_result_id"] == stored_independent["admission_result_id"] == ADMISSION_RESULT_ID, [stored_primary["admission_result_id"], stored_independent["admission_result_id"]], ADMISSION_RESULT_ID, "cross")
    audit.check("child claim nonbearing", stored_primary["claim_bearing"] is False and stored_independent["claim_bearing"] is False, [stored_primary["claim_bearing"], stored_independent["claim_bearing"]], [False, False], "scope")
    audit.check("child scope agreement", stored_primary["scope"] == stored_independent["scope"] == manifest["scope"], "identical", "identical", "cross")
    for key in ("rho", "det_E_S", "det_N_S", "exact_flow_species_coefficient", "macro_species_coefficient", "C4_local_tangent", "C4_block_witness", "C4_raw_EO_witness", "routed_seam_fixtures", "next_gate"):
        primary_value = canonical_cross_value(stored_primary["invariants"][key])
        independent_value = canonical_cross_value(stored_independent["invariants"][key])
        audit.check(f"cross invariant {key}", primary_value == independent_value, primary_value, independent_value, "cross")
    audit.check("children all assertions pass", all(row["status"] == "PASS" for row in stored_primary["assertions"] + stored_independent["assertions"]), "all PASS", "all PASS", "children")
    audit.check("child counts all pass", primary_summary["passed"] == primary_summary["total"] and independent_summary["passed"] == independent_summary["total"], [primary_summary, independent_summary], "passed equals total", "children")

    for result, label in ((stored_primary, "primary"), (stored_independent, "independent")):
        for source_name, recorded in result["source_sha256"].items():
            if source_name == "script":
                path = PRIMARY if label == "primary" else INDEPENDENT
            elif source_name == "parent_script":
                path = REPO / "codes/foundations/pre_a_cp1_cl8_interacting_two_arm_work_route_split.py"
            elif source_name == "manifest":
                path = MANIFEST
            elif source_name == "certificate":
                path = CERTIFICATE
            elif source_name == "admission":
                path = ADMISSION
            elif source_name == "evidence":
                path = EVIDENCE
            else:
                matches = list((REPO / "strategy").glob(source_name + ".json"))
                if not matches:
                    continue
                path = matches[0]
            audit.check(f"{label} hash {source_name}", recorded == sha256(path), recorded, sha256(path), "hashes")

    audit.check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest negatives", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "manifest")
    audit.check("admission no selection", admission["exact_admission_vector"]["round1_decisive_selection_authorized"] is False and admission["exact_admission_vector"]["pre_a_exit_conditions_met"] is False, admission["exact_admission_vector"], "both false", "admission")
    audit.check("evidence not frozen", evidence["versioning_policy"]["charter_complete_freeze"] is False, evidence["versioning_policy"]["charter_complete_freeze"], False, "admission")

    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    exploration_text = EXPLORATION.read_text(encoding="utf-8")
    todo = json.loads(TODO.read_text(encoding="utf-8"))
    proof_map_md = PROOF_MAP_MD.read_text(encoding="utf-8")
    proof_map_json = json.loads(PROOF_MAP_JSON.read_text(encoding="utf-8"))
    for negative_id in NEGATIVE_IDS:
        audit.check(f"negative registered {negative_id}", negative_id in registry_text, registry_text.find(negative_id), ">=0", "records")
    audit.check("macro result explored", RESULT_ID in exploration_text, exploration_text.find(RESULT_ID), ">=0", "records")
    audit.check("admission result explored", ADMISSION_RESULT_ID in exploration_text, exploration_text.find(ADMISSION_RESULT_ID), ">=0", "records")
    task_054 = next(item for item in todo["tasks"] if item["id"] == "T-054")
    task_050 = next(item for item in todo["tasks"] if item["id"] == "T-050")
    audit.check("T054 remains in progress", task_054["status"] == "in_progress", task_054["status"], "in_progress", "records")
    audit.check("T054 primary next gate recorded", admission["round1_primary_next_gate"] in task_054["note"], task_054["note"], admission["round1_primary_next_gate"], "records")
    audit.check("T050 remains backlog", task_050["status"] == "backlog", task_050["status"], "backlog", "records")
    audit.check("T050 parked priority recorded", "parked" in task_050["note"].lower() and "Pre-A" in task_050["note"], task_050["note"], "parked and Pre-A", "records")
    audit.check("proof map result", RESULT_ID in proof_map_md and RESULT_ID in json.dumps(proof_map_json, sort_keys=True), "present", "present", "generated")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"proof map negative {negative_id}", negative_id in proof_map_md and negative_id in json.dumps(proof_map_json, sort_keys=True), "present", "present", "generated")
    audit.check("all-k seam closed", manifest["scope"]["general_k_routed_periodic_cylinder_seam_intertwiner"] is True, manifest["scope"]["general_k_routed_periodic_cylinder_seam_intertwiner"], True, "scope")
    audit.check("universal quadratic and zero-centered Gaussian rejected", manifest["scope"]["universal_periodic_positive_quadratic_or_zero_centered_Gaussian_state"] is False, manifest["scope"]["universal_periodic_positive_quadratic_or_zero_centered_Gaussian_state"], False, "scope")
    audit.check("no C6 advancement", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "scope")
    audit.check("no Pre-A closure", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "scope")
    audit.check("no Sector-A change", manifest["scope"]["Sector_A_changed"] is False, manifest["scope"]["Sector_A_changed"], False, "scope")

    integrated_count = len(audit.rows)
    child_count = stored_primary["assertion_summary"]["total"] + stored_independent["assertion_summary"]["total"]
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "admission_result_id": ADMISSION_RESULT_ID,
        "negative_ids": NEGATIVE_IDS,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "child_results": {"primary": str(PRIMARY_STORED.relative_to(REPO)).replace("\\", "/"), "independent": str(INDEPENDENT_STORED.relative_to(REPO)).replace("\\", "/")},
        "child_assertions": {"primary": stored_primary["assertion_summary"], "independent": stored_independent["assertion_summary"]},
        "assertions": audit.rows,
        "assertion_summary": {"passed": integrated_count, "total": integrated_count},
        "total_evidence_checks": child_count + integrated_count,
        "scope": manifest["scope"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {"script": sha256(SCRIPT), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "admission": sha256(ADMISSION), "evidence": sha256(EVIDENCE)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} integrated: {summary['passed']}/{summary['total']} PASS; total evidence checks {payload['total_evidence_checks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
