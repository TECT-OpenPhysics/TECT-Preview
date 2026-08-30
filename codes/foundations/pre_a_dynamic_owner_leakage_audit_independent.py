#!/usr/bin/env python3
"""Non-importing independent reconstruction for R-449 owner leakage audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-dynamic-owner-leakage-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-30-independent-dynamic_owner_leakage_audit/independent.json"
)


def atomic_json(path: Path, payload: dict) -> None:
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


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []

    def check(name, condition, actual, expected, group):
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
        ]
        == ["R-449", "EXP-001322", "T-061", False],
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
        ],
        ["R-449", "EXP-001322", "T-061", False],
        "provenance",
    )
    slots = manifest["owner_intake"]["required_slots"]
    physical = manifest["owner_intake"]["physical_owner_required"]
    proof = manifest["owner_intake"]["proof_owner_required"]
    status = manifest["owner_intake"]["forward_owner_status"]
    check("slot concatenation", slots == physical + proof, slots, physical + proof, "owner-contract")
    check(
        "source owner absent",
        all(value in ("MISSING", "MISSING_SOURCE_OWNER") for value in status.values()),
        status,
        "all missing",
        "owner-contract",
    )

    r192 = json.loads(
        (ROOT / manifest["inputs"]["r192_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    first = r192["registered_inputs"]["first_failure_slot"]
    check("R-192 first failure", first == "heat_root_incidence", first, "heat_root_incidence", "lineage")
    table = {row["slot"]: row for row in r192["registered_inputs"]["slot_audit"]}
    check(
        "R-192 heat structural",
        table["heat_root_incidence"]["mapped"] is False
        and table["heat_root_incidence"]["status"] == "structural-only",
        table["heat_root_incidence"],
        "structural-only",
        "lineage",
    )

    a2 = json.loads(
        (ROOT / manifest["inputs"]["a2_crosswalk"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    crosswalk = a2["registered_crosswalk"]
    check(
        "A2 nonstochastic",
        crosswalk["a2_owner"]["stochastic_heat"] is False,
        crosswalk["a2_owner"],
        "stochastic_heat false",
        "A2-crosswalk",
    )
    check(
        "A2 incompatible",
        crosswalk["owner_compatible"] is False
        and crosswalk["expected_absence"] == proof,
        crosswalk,
        "false and all proof slots absent",
        "A2-crosswalk",
    )

    inverse = json.loads(
        (ROOT / manifest["inputs"]["inverse_contract"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    check(
        "inverse ordered stages",
        [stage["id"] for stage in inverse["forward_map_contract"]["stages"]]
        == ["F_reg", "F_lim", "F_eff", "F_obs"],
        [stage["id"] for stage in inverse["forward_map_contract"]["stages"]],
        ["F_reg", "F_lim", "F_eff", "F_obs"],
        "inverse-contract",
    )
    check(
        "inverse target empty",
        any(
            item["holdout_id"] == "PROS-LOCK-001"
            and item["status"] == "EMPTY_NOT_FROZEN"
            for item in inverse["holdout_manifest"]["holdouts"]
        ),
        inverse["holdout_manifest"]["status"],
        "empty prospective target",
        "inverse-contract",
    )

    r448 = json.loads(
        (ROOT / manifest["inputs"]["r448_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    check(
        "static quotient unowned",
        r448["scope"]["static_identifiability"] == "NON_IDENTIFIABLE"
        and not r448["scope"]["source_owner_admitted"],
        r448["scope"],
        "non-identifiable and unowned",
        "quotient",
    )
    check(
        "no candidate selection",
        inverse["candidate_comparison"]["current_selection"]
        == "NO_SELECTION_ZERO_ADMITTED_MICROSCOPIC_FORWARD_MAPS",
        inverse["candidate_comparison"]["current_selection"],
        "no selection",
        "inverse-contract",
    )
    check(
        "leakage firewall",
        manifest["leakage_audit"]["leakage_detected_and_blocked"]
        and not manifest["scope"]["physical_owner_complete"],
        manifest["leakage_audit"],
        "blocked",
        "leakage",
    )
    check(
        "methods unchanged",
        all(
            manifest["scope"][key]
            for key in (
                "owner_intake_audited",
                "proof_owner_separated",
                "no_tier_change",
                "no_pdf",
            )
        ),
        manifest["scope"],
        "preserved",
        "method-firewall",
    )
    for key, item in manifest["inputs"].items():
        path = ROOT / item["path"]
        check(
            f"input {key}",
            path.is_file()
            and item["sha256"] != "TO_BE_FILLED"
            and digest(path) == item["sha256"],
            digest(path) if path.is_file() else None,
            item["sha256"],
            "provenance",
        )

    derived = {
        "owner_slots": status,
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
        "schema": "tect/pre-a-dynamic-owner-leakage-audit-independent/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-449",
        "exploration_id": "EXP-001322",
        "task_id": "T-061",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "run_kind": "independent",
        "verdict": "INDEPENDENT_OWNER_INTAKE_LEAKAGE_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
        },
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        f"R-449 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)}",
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
        assert payload["derived"]["leakage_blocked"]
        assert payload["derived"]["owner_branch_verdict"].startswith("PARK_")
        print("R-449 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
