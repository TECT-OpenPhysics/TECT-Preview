#!/usr/bin/env python3
"""Independent structural intake for the PAH-001 researcher hypothesis.

This lane deliberately imports neither ``pah001_intake`` nor the R-471 primary
module.  It reconstructs the fail-closed state and canonical core digest with
separate code, then reports the same claim-nonbearing structural boundary.
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
INTAKE = REPO / "strategy/pa-hyp/intake-v1.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_file(path: Path) -> str:
    return hash_bytes(path.read_bytes())


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise TypeError(f"expected JSON object: {path}")
    return value


def inside_repo(relative: str) -> Path:
    candidate = (REPO / relative).resolve()
    if candidate != REPO and REPO not in candidate.parents:
        raise ValueError(f"path outside repository: {relative}")
    return candidate


def store_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=True, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prefix_hash(path: Path, terminal_id: str) -> str:
    accumulated = bytearray()
    seen = False
    for raw_line in path.read_bytes().splitlines(keepends=True):
        accumulated.extend(raw_line)
        parsed = json.loads(raw_line.decode("utf-8"))
        if parsed.get("id") == terminal_id:
            seen = True
            break
    if not seen:
        raise AssertionError(f"missing append-only terminal id: {terminal_id}")
    return hash_bytes(bytes(accumulated))


def pinned_hash(name: str, specification: dict[str, Any]) -> str:
    path = inside_repo(specification["path"])
    if name == "pre_intake_direction_log":
        return prefix_hash(path, specification["last_record"])
    return hash_file(path)


def follow_pointer(root: Any, pointer: str) -> Any:
    if pointer == "":
        return root
    if type(pointer) is not str or not pointer.startswith("/"):
        raise ValueError(pointer)
    value = root
    for part in pointer[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        if type(value) is list:
            value = value[int(key)]
        elif type(value) is dict:
            value = value[key]
        else:
            raise TypeError(f"pointer enters scalar: {pointer}")
    return value


def independent_state(
    packet: dict[str, Any], owner_order: tuple[str, ...], stage_order: tuple[str, ...]
) -> str:
    source = packet.get("source_artifact")
    if type(source) is not dict:
        return "EMPTY_OWNER_ARTIFACT"
    source_path = source.get("path")
    source_hash = source.get("sha256")
    if (
        type(source_path) is not str
        or not source_path.strip()
        or type(source_hash) is not str
        or SHA256_RE.fullmatch(source_hash) is None
    ):
        return "EMPTY_OWNER_ARTIFACT"
    slots = packet.get("owner_slot_status")
    if (
        type(slots) is not dict
        or set(slots) != set(owner_order)
        or any(slots.get(name) is not True for name in owner_order)
    ):
        return "PARTIAL_OWNER_PACKET"
    stages = packet.get("inverse_stage_status")
    if type(stages) is not dict or set(stages) != set(stage_order):
        return "OWNER_PACKET_HASHED"
    if any(stages[name] is not True for name in stage_order):
        return "OWNER_PACKET_HASHED"
    locks = (
        "candidate_neutral_estimand_frozen",
        "immutable_scorer_frozen",
        "prospective_holdout_frozen",
    )
    if any(packet.get(name) is not True for name in locks):
        return "FORWARD_MAP_COMPLETE"
    if packet.get("synthetic") is True or source.get("synthetic") is True:
        return "CONTRACT_TEST_ONLY_COMPLETE"
    return (
        "SCORING_ADMITTED"
        if packet.get("methods_unchanged") is True
        else "FORWARD_MAP_COMPLETE"
    )


def make_packet(intake: dict[str, Any]) -> dict[str, Any]:
    derived = json.loads(json.dumps(intake["derived_r471_packet"]))
    source = intake["source_artifact"]
    derived["source_artifact"] = {
        "path": source["path"],
        "sha256": source["sha256"],
        "synthetic": source["synthetic_fixture"],
    }
    return derived


def rebuild_core(
    intake: dict[str, Any],
    source: dict[str, Any],
    r471: dict[str, Any],
    state: str,
    intake_hash: str,
    source_hash: str,
    r471_hash: str,
) -> dict[str, Any]:
    owners = [entry["id"] for entry in source["r471_owner_slots"]]
    details = [entry["slot"] for entry in source["r192_detailed_bindings"]]
    stages = [entry["id"] for entry in r471["inverse_map_stages"]]
    derived = intake["derived_r471_packet"]
    boundary = intake["admission_boundary"]
    provenance = source["provenance"]
    interpretation = source["interpretive_boundary"]
    return {
        "authority": {
            "intake_sha256": intake_hash,
            "r471_sha256": r471_hash,
            "source_path": intake["source_artifact"]["path"],
            "source_sha256": source_hash,
        },
        "boundary": {
            "event_horizon_identity": interpretation["event_horizon_identity"],
            "physical_authority": provenance["physical_authority"],
            "physical_owner_admitted": boundary["physical_owner_admitted"],
            "pre_a_identity": interpretation["pre_a_identity"],
            "production_admission": "NONE",
            "provenance_class": provenance["class"],
            "synthetic_fixture": provenance["synthetic_fixture"],
        },
        "identity": {
            "candidate_id": source["candidate_id"],
            "claim_id": intake["claim_id"],
            "exploration_id": intake["exploration_id"],
            "packet_id": source["packet_id"],
            "result_id": intake["result_id"],
            "task_id": intake["task_id"],
            "version": source["version"],
        },
        "orders": {
            "inverse_stages": stages,
            "r192_details": details,
            "r471_owners": owners,
        },
        "state": {
            "inverse_stage_status": {
                stage: derived["inverse_stage_status"][stage] for stage in stages
            },
            "physical_projection_admitted": boundary["physical_projection_admitted"],
            "prospective_validated": boundary["prospective_validated"],
            "scoring_admitted": boundary["scoring_admitted"],
            "structural_state": state,
            "structurally_registered_candidate_count": boundary[
                "structurally_registered_candidate_count"
            ],
        },
    }


def digest_core(core: dict[str, Any]) -> str:
    raw = json.dumps(
        core, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hash_bytes(raw)


def run(output: Path | None = None) -> dict[str, Any]:
    intake = read_object(INTAKE)
    source_path = inside_repo(intake["source_artifact"]["path"])
    source = read_object(source_path)
    r471_spec = intake["authority_pins"]["r471"]
    r471_path = inside_repo(r471_spec["path"])
    r471 = read_object(r471_path)
    assertions: list[dict[str, Any]] = []

    def assert_equal(name: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append(
            {"name": name, "status": "PASS", "actual": actual, "expected": expected}
        )

    assert_equal("source file exists", source_path.is_file(), True)
    source_hash = hash_file(source_path)
    intake_hash = hash_file(INTAKE)
    r471_hash = hash_file(r471_path)
    assert_equal("source hash", source_hash, intake["source_artifact"]["sha256"])
    assert_equal("R-471 hash", r471_hash, r471_spec["sha256"])
    assert_equal("result id", intake["result_id"], "R-476")
    assert_equal("exploration id", intake["exploration_id"], "EXP-001357")
    assert_equal("task id", intake["task_id"], "T-062")
    assert_equal("claim bearing", intake["claim_bearing"], False)

    independently_hashed: dict[str, str] = {}
    for name in sorted(intake["authority_pins"]):
        specification = intake["authority_pins"][name]
        actual = pinned_hash(name, specification)
        independently_hashed[name] = actual
        assert_equal(f"authority {name}", actual, specification["sha256"])

    provenance = source["provenance"]
    assert_equal("researcher provenance", provenance["class"], "RESEARCHER_HYPOTHESIS")
    assert_equal("not external", provenance["external_source"], False)
    assert_equal("constructed", provenance["constructed_hypothesis"], True)
    assert_equal("not fixture", provenance["synthetic_fixture"], False)
    assert_equal("not physical authority", provenance["physical_authority"], False)
    assert_equal("physical identity open", provenance["physical_identity"], "UNESTABLISHED")

    owner_order = tuple(entry["id"] for entry in source["r471_owner_slots"])
    expected_owners = tuple(intake["required_r471_owner_order"])
    r471_owners = tuple(entry["id"] for entry in r471["forward_owner_slots"])
    assert_equal("owner order source", owner_order, expected_owners)
    assert_equal("owner order R-471", r471_owners, expected_owners)
    assert_equal("owner uniqueness", len(set(owner_order)), len(owner_order))
    assert_equal(
        "owner scopes",
        sorted({entry["authority_scope"] for entry in source["r471_owner_slots"]}),
        ["RESEARCHER_HYPOTHESIS"],
    )

    detail_order = tuple(entry["slot"] for entry in source["r192_detailed_bindings"])
    assert_equal("R-192 order", detail_order, tuple(intake["required_r192_detail_order"]))
    pointer_values = tuple(
        follow_pointer(source, entry["pointer"])
        for entry in source["r192_detailed_bindings"]
    )
    assert_equal("R-192 pointer count", len(pointer_values), len(detail_order))
    assert_equal(
        "R-192 boundary statuses",
        sorted({entry["status"] for entry in source["r192_detailed_bindings"]}),
        ["CANDIDATE_DEFINITION_NOT_A13_COMPATIBILITY"],
    )

    packet = make_packet(intake)
    assert_equal("owner packet keys", sorted(packet["owner_slot_status"]), sorted(owner_order))
    assert_equal("all owner slots present", all(packet["owner_slot_status"].values()), True)
    stage_order = tuple(entry["id"] for entry in r471["inverse_map_stages"])
    assert_equal("stage packet keys", sorted(packet["inverse_stage_status"]), sorted(stage_order))
    assert_equal("all inverse stages false", any(packet["inverse_stage_status"].values()), False)
    state = independent_state(packet, owner_order, stage_order)
    assert_equal("independent structural state", state, intake["test_oracles"]["expected_structural_state"])
    assert_equal("manifest structural state", packet["r471_structural_state"], state)
    assert_equal("production admission", intake["test_oracles"]["expected_production_admission"], "NONE")

    boundary = intake["admission_boundary"]
    assert_equal("one structural candidate", boundary["structurally_registered_candidate_count"], 1)
    assert_equal("no finite consistency claim", boundary["finite_model_consistent"], False)
    assert_equal("no physical owner", boundary["physical_owner_admitted"], False)
    assert_equal("no physical projection", boundary["physical_projection_admitted"], False)
    assert_equal("no scoring", boundary["scoring_admitted"], False)
    assert_equal("no prospective validation", boundary["prospective_validated"], False)
    assert_equal("no gate change", boundary["gate_changed"], False)
    assert_equal("no scientific transition", boundary["scientific_transition"], False)

    interpretation = source["interpretive_boundary"]
    assert_equal("event horizon not claimed", interpretation["event_horizon_identity"], "NOT_CLAIMED")
    assert_equal("Pre-A not claimed", interpretation["pre_a_identity"], "NOT_CLAIMED")
    assert_equal("black-hole interior excluded", interpretation["not_a_black_hole_interior_model"], True)
    limits = source["ordered_limits"]
    limit_order = tuple(entry["id"] for entry in limits["order"])
    assert_equal("limit order unique", len(set(limit_order)), len(limit_order))
    assert_equal("limit interchange absent", limits["interchange_claimed"], False)
    assert_equal(
        "aperture before observation time",
        limit_order.index("APERTURE_COLLAPSE") < limit_order.index("OBSERVATION_TIME"),
        True,
    )
    assert_equal("continuum estimate absent", source["common_core_and_uniform_contract"]["continuum_uniform_estimate"], False)
    assert_equal("scorer unfrozen", source["inverse_map_status"]["immutable_scorer_frozen"], False)
    assert_equal("holdout unfrozen", source["inverse_map_status"]["prospective_holdout_frozen"], False)

    core = rebuild_core(
        intake, source, r471, state, intake_hash, source_hash, r471_hash
    )
    core_digest = digest_core(core)
    minimum = int(intake["test_oracles"]["independent_minimum_assertions"])
    assert_equal("independent assertion floor", len(assertions) + 1 >= minimum, True)

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-001-STRUCTURAL-INTAKE-INDEPENDENT",
        "claim_id": intake["claim_id"],
        "task_id": intake["task_id"],
        "result_id": intake["result_id"],
        "exploration_id": intake["exploration_id"],
        "packet_id": source["packet_id"],
        "candidate_id": source["candidate_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_admission": "NONE",
        "current_state": state,
        "structurally_registered_candidate_count": boundary[
            "structurally_registered_candidate_count"
        ],
        "physical_owner_admitted": False,
        "physical_projection_admitted": False,
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "core": core,
        "core_digest": core_digest,
        "assertion_count": len(assertions),
        "passed": len(assertions),
        "assertions": assertions,
        "evidence_level": "T0 / INDEPENDENT HASH-PINNED RESEARCHER-HYPOTHESIS STRUCTURAL INTAKE",
        "boundary": intake["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "intake_sha256": intake_hash,
            "source_sha256": source_hash,
            "authority_sha256": independently_hashed,
        },
    }
    if output is not None:
        store_json(output if output.is_absolute() else REPO / output, payload)
    print(
        f"PAH001 INTAKE INDEPENDENT PASS {len(assertions)}/{len(assertions)}; "
        f"state={state}; production=NONE; core={core_digest}"
    )
    return payload


def main() -> int:
    intake = read_object(INTAKE)
    default_output = inside_repo(intake["runs"]["independent"])
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--no-store", action="store_true")
    arguments = parser.parse_args()
    run(None if arguments.no_store else arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
