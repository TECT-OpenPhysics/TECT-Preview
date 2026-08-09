#!/usr/bin/env python3
"""Integrated repository verifier for EXP-000782."""

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
SLUG = "pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-FKG-INFRARED-CUSP-PHASE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-LOW-TEMPERATURE-DLR-PHASE-AND-COLLECTIVE-SOURCE-CUSP"
EXPLORATION_ID = "EXP-000782"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-Q3-PHASE-SIGN-AND-KMS-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


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
        timeout=120,
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

    with tempfile.TemporaryDirectory(prefix="tect-exp775-") as temporary:
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
        audit.check(f"{label} assertions", payload["assertions"]["passed"] == payload["assertions"]["total"], payload["assertions"], "all pass", "implementations")
        audit.check(f"{label} candidate", payload["candidate_id"] == CANDIDATE_ID, payload["candidate_id"], CANDIDATE_ID, "implementations")
        audit.check(f"{label} result", payload["result_id"] == RESULT_ID, payload["result_id"], RESULT_ID, "implementations")
        audit.check(f"{label} exploration", payload["exploration_id"] == EXPLORATION_ID, payload["exploration_id"], EXPLORATION_ID, "implementations")
        audit.check(f"{label} parent gate", payload["parent_gate"] == PARENT_GATE, payload["parent_gate"], PARENT_GATE, "implementations")
        audit.check(f"{label} next gate", payload["next_gate"] == NEXT_GATE, payload["next_gate"], NEXT_GATE, "implementations")
        audit.check(f"{label} claim nonbearing", payload["claim_bearing"] is False, payload["claim_bearing"], False, "implementations")

    audit.check("fresh primary stdout", "PRIMARY PASS" in primary_stdout, primary_stdout, "PRIMARY PASS", "implementations")
    audit.check("fresh independent stdout", "INDEPENDENT PASS" in independent_stdout, independent_stdout, "INDEPENDENT PASS", "implementations")
    audit.check("stored/fresh primary total", primary_stored["assertions"]["total"] == primary_fresh["assertions"]["total"], primary_stored["assertions"]["total"], primary_fresh["assertions"]["total"], "implementations")
    audit.check("stored/fresh independent total", independent_stored["assertions"]["total"] == independent_fresh["assertions"]["total"], independent_stored["assertions"]["total"], independent_fresh["assertions"]["total"], "implementations")
    audit.check("cross scope", primary_fresh["scope"] == independent_fresh["scope"] == manifest["scope"], [primary_fresh["scope"], independent_fresh["scope"]], manifest["scope"], "implementations")
    primary_spectrum = sorted(
        int(eigenvalue)
        for eigenvalue, multiplicity in primary_fresh["derived"]["q3_laplacian_spectrum"].items()
        for _ in range(multiplicity)
    )
    audit.check("Q3 spectra agree", primary_spectrum == independent_fresh["derived"]["q3_spectrum"], primary_spectrum, independent_fresh["derived"]["q3_spectrum"], "implementations")
    audit.check("Watson constant", math.isclose(primary_fresh["derived"]["watson_I3"], 0.505462019717326, rel_tol=0.0, abs_tol=1e-14), primary_fresh["derived"]["watson_I3"], 0.505462019717326, "implementations")
    audit.check("independent Watson diagnostic", abs(independent_fresh["derived"]["watson_richardson_diagnostic"] - primary_fresh["derived"]["watson_I3"]) < 3e-6, independent_fresh["derived"]["watson_richardson_diagnostic"], primary_fresh["derived"]["watson_I3"], "implementations")
    audit.check("exact I3 L2", independent_fresh["derived"]["exact_I3_L2"] == "29/96", independent_fresh["derived"]["exact_I3_L2"], "29/96", "implementations")
    audit.check("exact I3 L4", independent_fresh["derived"]["exact_I3_L4"] == "1517/3840", independent_fresh["derived"]["exact_I3_L4"], "1517/3840", "implementations")

    for key in (
        "continuous_loop_FKG",
        "spatial_reflection_positivity",
        "collective_double_commutator_moment_bound",
        "Falk_Bruch_local_Duhamel_bound",
        "collective_infrared_bound",
        "strict_collective_source_pressure_cusp",
        "distinct_parity_related_tangent_DLR_states",
        "positive_lambda_DLR_phase_transition",
    ):
        audit.check(f"proved scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in (
        "phase_for_all_positive_lambda_parameters",
        "tangent_states_extreme",
        "Cstar_pure_states",
        "spatial_clustering",
        "infinite_volume_real_time_dynamics",
        "algebraic_KMS_for_preexisting_dynamics",
        "ground_state_phase",
        "uniform_spectral_gap",
        "continuum_regulator_removal",
        "physical_empty_space_reference",
        "below_empty_space",
        "C6_advanced",
        "Pre_A_complete",
    ):
        audit.check(f"open scope {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("explicit method boundary", "inconclusive" in manifest["explicit_phase_regime"]["method_boundary"], manifest["explicit_phase_regime"]["method_boundary"], "inconclusive", "scope")

    expected_paths = [MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, Path(__file__).resolve(), PRIMARY_STORED, INDEPENDENT_STORED]
    for path in expected_paths:
        audit.check(f"file exists {path.name}", path.is_file(), path, "file", "files")
        audit.check(f"file nonempty {path.name}", path.stat().st_size > 100, path.stat().st_size, ">100", "files")
    for label, stored in (("primary", primary_stored), ("independent", independent_stored)):
        audit.check(f"manifest hash {label}", stored["files"]["manifest_sha256"] == portable_sha256(MANIFEST), stored["files"]["manifest_sha256"], portable_sha256(MANIFEST), "files")
        audit.check(f"certificate hash {label}", stored["files"]["certificate_sha256"] == portable_sha256(CERTIFICATE), stored["files"]["certificate_sha256"], portable_sha256(CERTIFICATE), "files")

    explorations = jsonl_records(REPO / "explorations/log.jsonl")
    matches = [record for record in explorations if record.get("id") == EXPLORATION_ID]
    audit.check("one exploration record", len(matches) == 1, len(matches), 1, "records")
    exploration = matches[0]
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration result", RESULT_ID in exploration["finding"], exploration["finding"], RESULT_ID, "records")
    audit.check("exploration next gate", NEXT_GATE in exploration["next_action"], exploration["next_action"], NEXT_GATE, "records")

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
    claims_md = (REPO / "CLAIMS.md").read_text(encoding="utf-8")

    audit.check("parent gate present", PARENT_GATE in gates, PARENT_GATE in gates, True, "records")
    audit.check("parent partially resolved", EXPLORATION_ID in gates and "PARTIALLY RESOLVED" in gates, EXPLORATION_ID in gates, True, "records")
    audit.check("successor gate present", NEXT_GATE in gates, NEXT_GATE in gates, True, "records")
    audit.check("strategy manifest", f"{SLUG}-manifest.json" in strategy_index, f"{SLUG}-manifest.json" in strategy_index, True, "records")
    audit.check("strategy result", RESULT_ID in strategy_index, RESULT_ID in strategy_index, True, "records")
    audit.check("prior art exploration", EXPLORATION_ID in prior_art, EXPLORATION_ID in prior_art, True, "records")
    audit.check("prior art no priority", "No full-chain counterpart was located" in prior_art and "world-first" in prior_art, "No full-chain counterpart was located" in prior_art, True, "records")
    for negative_id in manifest["reused_negative_ids"]:
        audit.check(f"reused negative {negative_id}", negative_id in negative_registry, negative_id in negative_registry, True, "records")

    tasks = todo.get("tasks", todo if isinstance(todo, list) else [])
    task_matches = [task for task in tasks if task.get("id") == "T-054"]
    audit.check("T-054 unique", len(task_matches) == 1, len(task_matches), 1, "records")
    task = task_matches[0]
    audit.check("T-054 in progress", task["status"] == "in_progress", task["status"], "in_progress", "records")
    audit.check("T-054 successor", task["gate"] == NEXT_GATE, task["gate"], NEXT_GATE, "records")
    audit.check("T-054 EXP775", EXPLORATION_ID in task["note"], task["note"], EXPLORATION_ID, "records")

    changelog_matches = [entry for entry in changelog if EXPLORATION_ID.lower() in entry.get("header", "").lower() or EXPLORATION_ID.lower() in entry.get("raw", "").lower()]
    audit.check("changelog unique", len(changelog_matches) == 1, len(changelog_matches), 1, "records")
    audit.check("changelog manifest", f"strategy/{SLUG}-manifest.json" in changelog_matches[0]["notes"], changelog_matches[0]["notes"], f"strategy/{SLUG}-manifest.json", "records")

    relative_paths = (
        f"strategy/{SLUG}-manifest.json",
        f"strategy/{SLUG}-certificate-260804.md",
        "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split.py",
        "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py",
        "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_verify.py",
    )
    for relative in relative_paths:
        audit.check(f"catalog markdown {relative}", relative in catalog_md, relative in catalog_md, True, "generated")
        audit.check(f"catalog json {relative}", relative in catalog_json_text, relative in catalog_json_text, True, "generated")
    for label, needle in (("exploration", EXPLORATION_ID), ("result", RESULT_ID), ("successor", NEXT_GATE)):
        audit.check(f"proof map {label}", needle in proof_map_md and needle in proof_map_json_text, [needle in proof_map_md, needle in proof_map_json_text], [True, True], "generated")
    audit.check("CLAIMS includes C6", claims_md.count("C6-SPACETIME-SIGNATURE") >= 1, claims_md.count("C6-SPACETIME-SIGNATURE"), ">=1", "generated")

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000782 INTEGRATED PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
