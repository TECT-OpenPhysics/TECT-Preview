#!/usr/bin/env python3
"""Independent recomputation of the P1 admission firewall.

This lane intentionally does not import the primary implementation.  It uses
different set/order checks so a copied assertion cannot mask a contract error.
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
    "2026-08-31-independent-p1-owner-map-admission/independent.json"
)
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def status(packet: dict[str, Any], slots: tuple[str, ...], stages: tuple[str, ...]) -> str:
    source = packet.get("source_artifact")
    if not isinstance(source, dict):
        return "EMPTY_OWNER_ARTIFACT"
    path = source.get("path")
    digest = source.get("sha256")
    if not isinstance(path, str) or not path.strip() or not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        return "EMPTY_OWNER_ARTIFACT"
    slot_values = packet.get("owner_slot_status")
    if not isinstance(slot_values, dict) or set(slot_values) != set(slots) or any(slot_values.get(item) is not True for item in slots):
        return "PARTIAL_OWNER_PACKET"
    stage_values = packet.get("inverse_stage_status")
    if not isinstance(stage_values, dict) or set(stage_values) != set(stages):
        return "OWNER_PACKET_HASHED"
    for item in stages:
        if stage_values[item] is not True:
            return "OWNER_PACKET_HASHED"
    if not all(packet.get(name) is True for name in ("candidate_neutral_estimand_frozen", "immutable_scorer_frozen", "prospective_holdout_frozen")):
        return "FORWARD_MAP_COMPLETE"
    if packet.get("synthetic") is True or source.get("synthetic") is True:
        return "CONTRACT_TEST_ONLY_COMPLETE"
    return "SCORING_ADMITTED" if packet.get("methods_unchanged") is True else "FORWARD_MAP_COMPLETE"


def fixture(slots: tuple[str, ...], stages: tuple[str, ...], *, synthetic: bool) -> dict[str, Any]:
    return {
        "source_artifact": {"path": "fixture://owner-contract", "sha256": "b" * 64, "synthetic": synthetic},
        "owner_slot_status": {item: True for item in slots},
        "inverse_stage_status": {item: True for item in stages},
        "candidate_neutral_estimand_frozen": True,
        "immutable_scorer_frozen": True,
        "prospective_holdout_frozen": True,
        "methods_unchanged": True,
        "synthetic": synthetic,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    slots = tuple(item["id"] for item in manifest["forward_owner_slots"])
    stages = tuple(item["id"] for item in manifest["inverse_map_stages"])
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    check("manifest identity", (manifest["result_id"], manifest["exploration_id"], manifest["task_id"]) == ("R-471", "EXP-001346", "T-061"), [manifest["result_id"], manifest["exploration_id"], manifest["task_id"]], ["R-471", "EXP-001346", "T-061"])
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", [manifest["claim_bearing"], manifest["tier"]], [False, "T0"])
    check("methods preserved", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")
    for authority in manifest["authorities"]:
        path = REPO / authority["path"]
        check(f"authority {authority['path']}", path.is_file() and sha(path) == authority["sha256"], sha(path) if path.is_file() else "MISSING", authority["sha256"])
    check("slot ids unique", len(set(slots)) == len(slots), slots, "unique")
    check("stage ids unique", len(set(stages)) == len(stages), stages, "unique")
    check("stage orders contiguous", [item["order"] for item in manifest["inverse_map_stages"]] == list(range(1, len(stages) + 1)), [item["order"] for item in manifest["inverse_map_stages"]], list(range(1, len(stages) + 1)))

    current = json.loads(json.dumps(manifest["current_snapshot"]))
    current_state = status(current, slots, stages)
    check("current state empty", current_state == "EMPTY_OWNER_ARTIFACT", current_state, "EMPTY_OWNER_ARTIFACT")
    check("current has no admitted candidate", manifest["admission_state_machine"]["current_admitted_candidate_count"] == 0 and current["admitted_candidate_count"] == 0, current["admitted_candidate_count"], 0)

    test_packet = fixture(slots, stages, synthetic=True)
    check("complete fixture is test-only", status(test_packet, slots, stages) == "CONTRACT_TEST_ONLY_COMPLETE", status(test_packet, slots, stages), "CONTRACT_TEST_ONLY_COMPLETE")
    test_packet["inverse_stage_status"][stages[1]] = False
    check("missing middle stage blocks", status(test_packet, slots, stages) == "OWNER_PACKET_HASHED", status(test_packet, slots, stages), "OWNER_PACKET_HASHED")
    test_packet = fixture(slots, stages, synthetic=True)
    test_packet["owner_slot_status"].pop(slots[-1])
    check("missing final owner slot blocks", status(test_packet, slots, stages) == "PARTIAL_OWNER_PACKET", status(test_packet, slots, stages), "PARTIAL_OWNER_PACKET")
    test_packet = fixture(slots, stages, synthetic=False)
    test_packet["source_artifact"]["sha256"] = "not-a-sha"
    check("malformed hash blocks", status(test_packet, slots, stages) == "EMPTY_OWNER_ARTIFACT", status(test_packet, slots, stages), "EMPTY_OWNER_ARTIFACT")
    test_packet = fixture(slots, stages, synthetic=False)
    test_packet["prospective_holdout_frozen"] = False
    check("holdout required", status(test_packet, slots, stages) == "FORWARD_MAP_COMPLETE", status(test_packet, slots, stages), "FORWARD_MAP_COMPLETE")

    core = {
        "slots": slots,
        "stages": stages,
        "current_state": current_state,
        "synthetic_state": status(fixture(slots, stages, synthetic=True), slots, stages),
        "authority_hashes": {item["path"]: item["sha256"] for item in manifest["authorities"]},
    }
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "P1-OWNER-MAP-ADMISSION-INDEPENDENT",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_admission": "NONE",
        "current_state": current_state,
        "synthetic_fixture_state": core["synthetic_state"],
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "core_digest": hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if output:
        write_json(output if output.is_absolute() else REPO / output, payload)
    print(f"P1 OWNER/MAP ADMISSION INDEPENDENT PASS {len(checks)}/{len(checks)}; current={current_state}; synthetic={core['synthetic_state']}")
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
