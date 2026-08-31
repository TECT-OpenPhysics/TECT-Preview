#!/usr/bin/env python3
"""Primary fail-closed admission test for the unchanged P1 owner/map contract.

This is a contract test, not a physical dynamics implementation.  It exercises
the existing T-054/T-059/T-061 owner order with synthetic packets only and
keeps the current production state empty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/p1-owner-map-admission-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-p1-owner-map-admission/primary.json"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def ordered_ids(manifest: dict[str, Any]) -> list[str]:
    return [item["id"] for item in manifest["forward_owner_slots"]]


def stage_ids(manifest: dict[str, Any]) -> list[str]:
    return [item["id"] for item in manifest["inverse_map_stages"]]


def production_state(packet: dict[str, Any], manifest: dict[str, Any]) -> str:
    """Return the fail-closed state for a packet.

    The function is deliberately structural.  A complete synthetic packet is
    a contract-test outcome and never a production admission.
    """

    source = packet.get("source_artifact", {})
    source_path = source.get("path", "")
    source_hash = source.get("sha256", "")
    if not isinstance(source_path, str) or not source_path.strip():
        return "EMPTY_OWNER_ARTIFACT"
    if not isinstance(source_hash, str) or SHA256_RE.fullmatch(source_hash) is None:
        return "EMPTY_OWNER_ARTIFACT"

    slot_status = packet.get("owner_slot_status", {})
    slots = ordered_ids(manifest)
    present = sum(bool(slot_status.get(slot, False)) for slot in slots)
    if present != len(slots):
        return "PARTIAL_OWNER_PACKET"

    stage_status = packet.get("inverse_stage_status", {})
    stages = stage_ids(manifest)
    for stage in stages:
        if not bool(stage_status.get(stage, False)):
            return "OWNER_PACKET_HASHED"

    if not bool(packet.get("candidate_neutral_estimand_frozen", False)):
        return "FORWARD_MAP_COMPLETE"
    if not bool(packet.get("immutable_scorer_frozen", False)):
        return "FORWARD_MAP_COMPLETE"
    if not bool(packet.get("prospective_holdout_frozen", False)):
        return "FORWARD_MAP_COMPLETE"
    if packet.get("synthetic", False) or source.get("synthetic", False):
        return "CONTRACT_TEST_ONLY_COMPLETE"
    if packet.get("methods_unchanged") is not True:
        return "FORWARD_MAP_COMPLETE"
    return "SCORING_ADMITTED"


def current_packet(manifest: dict[str, Any]) -> dict[str, Any]:
    snapshot = manifest["current_snapshot"]
    return json.loads(json.dumps(snapshot))


def complete_synthetic_packet(manifest: dict[str, Any]) -> dict[str, Any]:
    slots = {slot: True for slot in ordered_ids(manifest)}
    stages = {stage: True for stage in stage_ids(manifest)}
    return {
        "source_artifact": {
            "path": "fixture://owner-complete-contract-only",
            "sha256": "a" * 64,
            "synthetic": True,
        },
        "owner_slot_status": slots,
        "inverse_stage_status": stages,
        "prospective_holdout_frozen": True,
        "candidate_neutral_estimand_frozen": True,
        "immutable_scorer_frozen": True,
        "methods_unchanged": True,
        "synthetic": True,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {"name": name, "status": "PASS", "actual": actual, "expected": expected}
        )

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]]
        == ["R-471", "EXP-001346", "T-061", False],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]],
        ["R-471", "EXP-001346", "T-061", False],
    )
    check(
        "method preservation",
        all(manifest["method_preservation"].values()),
        manifest["method_preservation"],
        "all preservation flags true",
    )
    authorities = manifest["authorities"]
    for authority in authorities:
        path = REPO / authority["path"]
        check(
            f"authority hash {authority['path']}",
            path.is_file() and digest(path) == authority["sha256"],
            digest(path) if path.is_file() else "MISSING",
            authority["sha256"],
        )

    slots = ordered_ids(manifest)
    classes = [item["owner_class"] for item in manifest["forward_owner_slots"]]
    check("owner slot order", slots == [
        "generator_or_transfer", "state", "physical_projection", "time_boundary",
        "heat_root_incidence", "root_filtration", "conditional_replicas",
        "raw_current_spatial_intertwiner", "production_one_use_q_ledger",
    ], slots, "existing T-054 owner order")
    check(
        "owner slot uniqueness",
        len(slots) == len(set(slots)) and len(slots) == len(classes),
        slots,
        "unique ordered slots",
    )
    check(
        "physical proof partition",
        classes[:4] == ["physical"] * 4 and classes[4:] == ["proof"] * (len(classes) - 4),
        classes,
        "four physical then proof slots",
    )

    stages = stage_ids(manifest)
    check(
        "inverse stage order",
        stages == ["F_reg", "F_lim", "F_eff", "F_obs"],
        stages,
        "F_reg/F_lim/F_eff/F_obs",
    )
    check(
        "stage ordinals",
        [item["order"] for item in manifest["inverse_map_stages"]] == list(range(1, len(stages) + 1)),
        [item["order"] for item in manifest["inverse_map_stages"]],
        list(range(1, len(stages) + 1)),
    )
    check(
        "state machine order",
        manifest["admission_state_machine"]["states"][: len(stages) - 1]
        == ["EMPTY_OWNER_ARTIFACT", "PARTIAL_OWNER_PACKET", "OWNER_PACKET_HASHED"],
        manifest["admission_state_machine"]["states"],
        "empty, partial, hashed prefix",
    )

    current = current_packet(manifest)
    check("current source empty", production_state(current, manifest) == "EMPTY_OWNER_ARTIFACT", production_state(current, manifest), "EMPTY_OWNER_ARTIFACT")
    check("current admitted count", manifest["admission_state_machine"]["current_admitted_candidate_count"] == 0 and current["admitted_candidate_count"] == 0, current["admitted_candidate_count"], 0)
    check("current slots all false", not any(current["owner_slot_status"].values()), current["owner_slot_status"], "all false")
    check("current stages all false", not any(current["inverse_stage_status"].values()), current["inverse_stage_status"], "all false")
    check("current holdout empty", current["prospective_holdout_frozen"] is False and current["immutable_scorer_frozen"] is False, current["prospective_holdout_frozen"], False)

    partial = complete_synthetic_packet(manifest)
    partial["owner_slot_status"][slots[-1]] = False
    partial_state = production_state(partial, manifest)
    check("partial packet blocked", partial_state == "PARTIAL_OWNER_PACKET", partial_state, "PARTIAL_OWNER_PACKET")

    complete = complete_synthetic_packet(manifest)
    complete_state = production_state(complete, manifest)
    check("synthetic complete is test-only", complete_state == "CONTRACT_TEST_ONLY_COMPLETE", complete_state, "CONTRACT_TEST_ONLY_COMPLETE")
    check("synthetic never production", complete_state not in {"SCORING_ADMITTED", "PROSPECTIVE_VALIDATED"}, complete_state, "not admitted")

    no_reg = complete_synthetic_packet(manifest)
    no_reg["synthetic"] = False
    no_reg["source_artifact"]["synthetic"] = False
    no_reg["inverse_stage_status"]["F_reg"] = False
    check("missing F_reg blocks", production_state(no_reg, manifest) == "OWNER_PACKET_HASHED", production_state(no_reg, manifest), "OWNER_PACKET_HASHED")

    no_holdout = complete_synthetic_packet(manifest)
    no_holdout["synthetic"] = False
    no_holdout["source_artifact"]["synthetic"] = False
    no_holdout["prospective_holdout_frozen"] = False
    check("missing holdout blocks scoring", production_state(no_holdout, manifest) == "FORWARD_MAP_COMPLETE", production_state(no_holdout, manifest), "FORWARD_MAP_COMPLETE")

    no_hash = complete_synthetic_packet(manifest)
    no_hash["synthetic"] = False
    no_hash["source_artifact"]["synthetic"] = False
    no_hash["source_artifact"]["sha256"] = ""
    check("missing source hash blocks", production_state(no_hash, manifest) == "EMPTY_OWNER_ARTIFACT", production_state(no_hash, manifest), "EMPTY_OWNER_ARTIFACT")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "P1-OWNER-MAP-ADMISSION-PRIMARY",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_admission": "NONE",
        "current_state": production_state(current, manifest),
        "synthetic_fixture_state": complete_state,
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "manifest_sha256": digest(MANIFEST),
            "source_authority_sha256": {item["path"]: item["sha256"] for item in authorities},
        },
    }
    if output:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"P1 OWNER/MAP ADMISSION PRIMARY PASS {len(checks)}/{len(checks)}; current={payload['current_state']}; synthetic={complete_state}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(None if args.no_store else args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
