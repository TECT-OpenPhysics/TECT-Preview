#!/usr/bin/env python3
"""Primary owner-intake and physical/proof leakage audit for R-449."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-dynamic-owner-leakage-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-30-primary-dynamic_owner_leakage_audit/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(
        name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": actual,
                "expected": expected,
            }
        )

    check(
        "identity",
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
        ]
        == ["R-449", "EXP-001322", "T-061", False, "T0"],
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
        ],
        ["R-449", "EXP-001322", "T-061", False, "T0"],
        "provenance",
    )
    check(
        "method preservation",
        all(
            manifest["scope"][key]
            for key in (
                "owner_intake_audited",
                "proof_owner_separated",
                "no_new_negative",
                "no_tier_change",
                "no_pdf",
            )
        ),
        manifest["scope"],
        "required preservation flags true",
        "method-firewall",
    )

    required = manifest["owner_intake"]["required_slots"]
    physical = manifest["owner_intake"]["physical_owner_required"]
    proof = manifest["owner_intake"]["proof_owner_required"]
    statuses = manifest["owner_intake"]["forward_owner_status"]
    check(
        "owner slots partition",
        set(physical).isdisjoint(proof) and required == physical + proof,
        required,
        "physical plus proof slots",
        "owner-contract",
    )
    check(
        "all source-owner slots missing",
        all(value in ("MISSING_SOURCE_OWNER", "MISSING") for value in statuses.values()),
        statuses,
        "no slot admitted",
        "owner-contract",
    )
    check(
        "R-192 first failure",
        manifest["source_crosswalk"]["r192"]["first_failure_slot"]
        == "heat_root_incidence",
        manifest["source_crosswalk"]["r192"]["first_failure_slot"],
        "heat_root_incidence",
        "lineage",
    )

    r192 = json.loads(
        (ROOT / manifest["inputs"]["r192_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    r192_slots = {
        item["slot"]: item for item in r192["registered_inputs"]["slot_audit"]
    }
    check(
        "R-192 structural heat map",
        r192_slots["heat_root_incidence"]["mapped"] is False
        and r192_slots["heat_root_incidence"]["status"] == "structural-only",
        r192_slots["heat_root_incidence"],
        "unmapped structural-only",
        "lineage",
    )
    check(
        "R-192 q-ledger missing",
        r192_slots["source"]["mapped"] is False
        and r192_slots["source"]["status"] == "missing-q-ledger",
        r192_slots["source"],
        "missing q-ledger",
        "lineage",
    )

    a2 = json.loads(
        (ROOT / manifest["inputs"]["a2_crosswalk"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cross = a2["registered_crosswalk"]
    owner = cross["a2_owner"]
    check(
        "A2 deterministic flow",
        owner["stochastic_heat"] is False and "deterministic" in owner["flow"],
        owner,
        "deterministic non-stochastic flow",
        "A2-crosswalk",
    )
    check(
        "A2 incompatibility",
        cross["owner_compatible"] is False
        and cross["first_failure_slot"] == "heat_root_incidence",
        cross,
        "incompatible at first missing slot",
        "A2-crosswalk",
    )
    check(
        "A2 expected absence",
        list(cross["expected_absence"]) == proof,
        cross["expected_absence"],
        proof,
        "A2-crosswalk",
    )

    inverse = json.loads(
        (ROOT / manifest["inputs"]["inverse_contract"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    check(
        "inverse stage order",
        [stage["id"] for stage in inverse["forward_map_contract"]["stages"]]
        == manifest["inverse_contract_audit"]["required_stages"],
        [stage["id"] for stage in inverse["forward_map_contract"]["stages"]],
        manifest["inverse_contract_audit"]["required_stages"],
        "inverse-contract",
    )
    check(
        "inverse missing-stage rule",
        inverse["forward_map_contract"]["missing_stage_rule"]
        == manifest["inverse_contract_audit"]["stage_rule"],
        inverse["forward_map_contract"]["missing_stage_rule"],
        manifest["inverse_contract_audit"]["stage_rule"],
        "inverse-contract",
    )
    check(
        "prospective holdout empty",
        inverse["holdout_manifest"]["status"].endswith("PROSPECTIVE_TARGET_EMPTY")
        and any(
            item["holdout_id"] == "PROS-LOCK-001"
            and item["status"] == "EMPTY_NOT_FROZEN"
            for item in inverse["holdout_manifest"]["holdouts"]
        ),
        inverse["holdout_manifest"]["status"],
        "prospective target empty",
        "inverse-contract",
    )
    check(
        "candidate selection empty",
        inverse["candidate_comparison"]["current_selection"]
        == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS",
        inverse["candidate_comparison"]["current_selection"],
        "zero admitted maps",
        "inverse-contract",
    )

    r448 = json.loads(
        (ROOT / manifest["inputs"]["r448_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    check(
        "R-448 quotient boundary",
        r448["scope"]["static_identifiability"] == "NON_IDENTIFIABLE"
        and r448["scope"]["source_owner_admitted"] is False
        and r448["scope"]["physical_identity"] is False,
        r448["scope"],
        "non-identifiable and unowned",
        "quotient",
    )

    program = json.loads(
        (ROOT / manifest["inputs"]["main_program"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    check(
        "programme active packet",
        program["current_work_packet"]["id"]
        == "P1-DYNAMIC-OWNER-OBSERVATION-MAP-001"
        and program["current_work_packet"]["status"] == "ACTIVE",
        program["current_work_packet"]["id"],
        "active P1 packet",
        "programme",
    )
    check(
        "programme next action preserved",
        "Continue unchanged T-054 forward owner intake"
        in program["current_work_packet"]["next_action"],
        program["current_work_packet"]["next_action"],
        "unchanged forward intake",
        "programme",
    )

    leakage = manifest["leakage_audit"]
    check(
        "physical proof separation",
        leakage["physical_owner_evidence"] == []
        and len(leakage["proof_owner_evidence"]) >= 1,
        leakage,
        "no physical evidence and proof comparators listed",
        "leakage",
    )
    check(
        "leakage blocked",
        leakage["leakage_detected_and_blocked"] is True
        and leakage["cross_lane_circular_support_forbidden"] is True,
        leakage,
        "blocked",
        "leakage",
    )
    check(
        "parked verdict",
        leakage["owner_branch_verdict"]
        == "PARK_OWNER_BRANCH_SURVIVING_STATIC_EQUIVALENCE_CLASS"
        and manifest["scope"]["candidate_selection"] is False,
        leakage["owner_branch_verdict"],
        "parked no selection",
        "verdict",
    )
    check(
        "downstream firewalls",
        all(
            manifest["scope"][key] is False
            for key in (
                "physical_owner_complete",
                "inverse_map_complete",
                "prospective_holdout_frozen",
                "pre_a_closed",
                "sector_a_closed",
                "c6_closed",
            )
        ),
        manifest["scope"],
        "all downstream closures false",
        "boundary",
    )

    for key, item in manifest["inputs"].items():
        path = ROOT / item["path"]
        check(
            f"input {key} hash",
            path.is_file()
            and item["sha256"] != "TO_BE_FILLED"
            and digest(path) == item["sha256"],
            digest(path) if path.is_file() else None,
            item["sha256"],
            "provenance",
        )
    for key, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(
            f"file {key} hash",
            path.is_file()
            and item["sha256"] != "TO_BE_FILLED"
            and digest(path) == item["sha256"],
            digest(path) if path.is_file() else None,
            item["sha256"],
            "provenance",
        )

    lean = ROOT / manifest["lean_crosscheck"]["path"]
    source = lean.read_text(encoding="utf-8")
    check(
        "Lean markers",
        all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]),
        manifest["lean_crosscheck"]["theorem_markers"],
        "all present",
        "Lean",
    )
    check(
        "Lean firewall",
        not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")),
        "forbidden tokens absent",
        "clean",
        "Lean",
    )

    derived = {
        "owner_slots": statuses,
        "first_failure_slot": "heat_root_incidence",
        "a2_owner_compatible": False,
        "a2_stochastic_heat": False,
        "r192_production_map_complete": False,
        "inverse_stages": manifest["source_crosswalk"]["inverse"],
        "prospective_lock": "EMPTY_NOT_FROZEN",
        "candidate_selection": "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS",
        "physical_owner_evidence": [],
        "proof_comparators": manifest["leakage_audit"]["proof_owner_evidence"],
        "leakage_blocked": True,
        "owner_branch_verdict": "PARK_OWNER_BRANCH_SURVIVING_STATIC_EQUIVALENCE_CLASS",
        "methods_preserved": True,
        "claim_bearing": False,
    }
    payload = {
        "schema": "tect/pre-a-dynamic-owner-leakage-audit-primary/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": manifest["status"],
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        f"R-449 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} "
        "owner=parked leakage=blocked",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "OWNER_INTAKE_LEAKAGE_AUDITED"
        assert (
            payload["derived"]["owner_branch_verdict"]
            == "PARK_OWNER_BRANCH_SURVIVING_STATIC_EQUIVALENCE_CLASS"
        )
        print("R-449 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
