#!/usr/bin/env python3
"""Primary structural intake for the PAH-001 researcher hypothesis.

This audit reuses the canonical R-471 ``production_state`` function.  Reaching
``OWNER_PACKET_HASHED`` means only that the hypothesis bytes and declared owner
interfaces are structurally complete.  It is not production or physical
admission and does not validate any theorem target in PAH-001.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
FOUNDATIONS = Path(__file__).resolve().parent
INTAKE = REPO / "strategy/pa-hyp/intake-v1.json"

if str(FOUNDATIONS) not in sys.path:
    sys.path.insert(0, str(FOUNDATIONS))

from p1_owner_map_admission_contract import production_state as r471_production_state


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def repo_path(relative: str) -> Path:
    path = (REPO / relative).resolve()
    if path != REPO and REPO not in path.parents:
        raise ValueError(f"repository path escape: {relative}")
    return path


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError(f"invalid JSON pointer: {pointer!r}")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise TypeError(f"pointer traverses scalar at {token!r}: {pointer}")
    return current


def append_only_prefix_digest(path: Path, last_record: str) -> str:
    """Hash raw bytes through one JSONL record, preserving original newlines."""

    prefix: list[bytes] = []
    found = False
    for line in path.read_bytes().splitlines(keepends=True):
        prefix.append(line)
        record = json.loads(line.decode("utf-8"))
        if record.get("id") == last_record:
            found = True
            break
    if not found:
        raise ValueError(f"append-only record not found: {last_record}")
    return sha256_bytes(b"".join(prefix))


def authority_digest(name: str, specification: dict[str, Any]) -> str:
    path = repo_path(specification["path"])
    if name == "pre_intake_direction_log":
        return append_only_prefix_digest(path, specification["last_record"])
    return sha256_file(path)


def build_r471_packet(intake: dict[str, Any]) -> dict[str, Any]:
    packet = deepcopy(intake["derived_r471_packet"])
    source = intake["source_artifact"]
    packet["source_artifact"] = {
        "path": source["path"],
        "sha256": source["sha256"],
        "synthetic": source["synthetic_fixture"],
    }
    return packet


def core_record(
    intake: dict[str, Any],
    source: dict[str, Any],
    r471: dict[str, Any],
    state: str,
    intake_hash: str,
    source_hash: str,
    r471_hash: str,
) -> dict[str, Any]:
    owner_order = [item["id"] for item in source["r471_owner_slots"]]
    detail_order = [item["slot"] for item in source["r192_detailed_bindings"]]
    stage_order = [item["id"] for item in r471["inverse_map_stages"]]
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
            "inverse_stages": stage_order,
            "r192_details": detail_order,
            "r471_owners": owner_order,
        },
        "state": {
            "inverse_stage_status": {
                item: derived["inverse_stage_status"][item] for item in stage_order
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


def canonical_digest(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return sha256_bytes(encoded)


def run(output: Path | None = None) -> dict[str, Any]:
    intake = load_json(INTAKE)
    source_path = repo_path(intake["source_artifact"]["path"])
    source = load_json(source_path)
    r471_specification = intake["authority_pins"]["r471"]
    r471_path = repo_path(r471_specification["path"])
    r471 = load_json(r471_path)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {"name": name, "status": "PASS", "actual": actual, "expected": expected}
        )

    check(
        "intake schema",
        intake["schema"] == "tect/pre-a-researcher-hypothesis-intake/1.0",
        intake["schema"],
        "tect/pre-a-researcher-hypothesis-intake/1.0",
    )
    check(
        "source schema",
        source["schema"] == "tect/pre-a-researcher-hypothesis/1.0",
        source["schema"],
        "tect/pre-a-researcher-hypothesis/1.0",
    )
    expected_identity = ["R-476", "EXP-001357", "T-062", "C6-SPACETIME-SIGNATURE"]
    actual_identity = [
        intake["result_id"],
        intake["exploration_id"],
        intake["task_id"],
        intake["claim_id"],
    ]
    check("intake identity", actual_identity == expected_identity, actual_identity, expected_identity)
    check(
        "claim nonbearing",
        intake["claim_bearing"] is False and intake["tier"] == "T0",
        [intake["claim_bearing"], intake["tier"]],
        [False, "T0"],
    )
    check(
        "source path identity",
        source_path.is_file() and source_path == repo_path(intake["files"]["source"]),
        str(source_path.relative_to(REPO)),
        intake["files"]["source"],
    )
    source_hash = sha256_file(source_path)
    check(
        "source raw-byte hash",
        source_hash == intake["source_artifact"]["sha256"],
        source_hash,
        intake["source_artifact"]["sha256"],
    )
    intake_hash = sha256_file(INTAKE)
    r471_hash = sha256_file(r471_path)
    check(
        "R-471 authority hash",
        r471_hash == r471_specification["sha256"],
        r471_hash,
        r471_specification["sha256"],
    )
    authority_hashes: dict[str, str] = {}
    for name, specification in intake["authority_pins"].items():
        actual = authority_digest(name, specification)
        authority_hashes[name] = actual
        check(
            f"authority hash {name}",
            actual == specification["sha256"],
            actual,
            specification["sha256"],
        )

    provenance = source["provenance"]
    overlay = intake["provenance_overlay"]["researcher_hypothesis_rule"]
    check("provenance class", provenance["class"] == "RESEARCHER_HYPOTHESIS", provenance["class"], "RESEARCHER_HYPOTHESIS")
    check("external source false", provenance["external_source"] is False, provenance["external_source"], False)
    check("constructed hypothesis true", provenance["constructed_hypothesis"] is True, provenance["constructed_hypothesis"], True)
    check("synthetic fixture false", provenance["synthetic_fixture"] is False, provenance["synthetic_fixture"], False)
    check("physical authority false", provenance["physical_authority"] is False, provenance["physical_authority"], False)
    check("physical identity unestablished", provenance["physical_identity"] == "UNESTABLISHED", provenance["physical_identity"], "UNESTABLISHED")
    check("L2 specification boundary", provenance["epistemic_layer"] == "L2_MODEL_SPECIFICATION_ONLY", provenance["epistemic_layer"], "L2_MODEL_SPECIFICATION_ONLY")
    check(
        "overlay provenance agreement",
        all(
            [
                overlay["external_source"] is provenance["external_source"],
                overlay["constructed_hypothesis"] is provenance["constructed_hypothesis"],
                overlay["synthetic_fixture"] is provenance["synthetic_fixture"],
                overlay["physical_authority"] is provenance["physical_authority"],
                overlay["physical_identity"] == provenance["physical_identity"],
            ]
        ),
        overlay,
        "matches source provenance",
    )
    check("method preservation", all(value is True for value in source["method_preservation"].values()), source["method_preservation"], "all true")
    check(
        "overlay keeps contracts unchanged",
        all(
            intake["provenance_overlay"][name] is True
            for name in (
                "r471_state_machine_unchanged",
                "r192_owner_order_unchanged",
                "existing_t054_method_unchanged",
            )
        ),
        intake["provenance_overlay"],
        "all unchanged flags true",
    )

    required_owner_order = intake["required_r471_owner_order"]
    source_owner_order = [item["id"] for item in source["r471_owner_slots"]]
    r471_owner_order = [item["id"] for item in r471["forward_owner_slots"]]
    check("source owner order", source_owner_order == required_owner_order, source_owner_order, required_owner_order)
    check("R-471 owner order", r471_owner_order == required_owner_order, r471_owner_order, required_owner_order)
    check("owner ids unique", len(set(source_owner_order)) == len(source_owner_order), source_owner_order, "unique")
    required_slot_fields = {"id", "kind", "status", "authority_scope", "domain", "codomain", "equation", "dependencies", "falsifier", "proof_status"}
    check(
        "owner slot field completeness",
        all(required_slot_fields <= set(item) for item in source["r471_owner_slots"]),
        [sorted(set(item)) for item in source["r471_owner_slots"]],
        sorted(required_slot_fields),
    )
    check(
        "owner slots researcher scoped",
        all(item["authority_scope"] == "RESEARCHER_HYPOTHESIS" for item in source["r471_owner_slots"]),
        [item["authority_scope"] for item in source["r471_owner_slots"]],
        "RESEARCHER_HYPOTHESIS",
    )
    check(
        "owner slot definitions nonempty",
        all(
            isinstance(item["equation"], str)
            and item["equation"].strip()
            and isinstance(item["domain"], str)
            and item["domain"].strip()
            and isinstance(item["codomain"], str)
            and item["codomain"].strip()
            for item in source["r471_owner_slots"]
        ),
        "all exact interface strings present",
        True,
    )

    required_detail_order = intake["required_r192_detail_order"]
    actual_detail_order = [item["slot"] for item in source["r192_detailed_bindings"]]
    check("R-192 detail order", actual_detail_order == required_detail_order, actual_detail_order, required_detail_order)
    resolved_bindings = [json_pointer(source, item["pointer"]) for item in source["r192_detailed_bindings"]]
    check("R-192 pointers resolve", len(resolved_bindings) == len(required_detail_order), len(resolved_bindings), len(required_detail_order))
    check(
        "R-192 compatibility boundary explicit",
        all(item["status"] == "CANDIDATE_DEFINITION_NOT_A13_COMPATIBILITY" for item in source["r192_detailed_bindings"]),
        [item["status"] for item in source["r192_detailed_bindings"]],
        "CANDIDATE_DEFINITION_NOT_A13_COMPATIBILITY",
    )
    check("structural acceptance flags", all(value is True for value in intake["structural_acceptance"].values()), intake["structural_acceptance"], "all true")

    packet = build_r471_packet(intake)
    check("derived owner keys exact", set(packet["owner_slot_status"]) == set(required_owner_order), sorted(packet["owner_slot_status"]), sorted(required_owner_order))
    check("derived owners all present", all(packet["owner_slot_status"].get(item) is True for item in required_owner_order), packet["owner_slot_status"], "all true")
    stage_order = [item["id"] for item in r471["inverse_map_stages"]]
    check("derived stage keys exact", set(packet["inverse_stage_status"]) == set(stage_order), sorted(packet["inverse_stage_status"]), sorted(stage_order))
    check("inverse stages all closed", all(packet["inverse_stage_status"][item] is False for item in stage_order), packet["inverse_stage_status"], "all false")
    check(
        "scoring locks empty",
        all(
            packet[name] is False
            for name in (
                "candidate_neutral_estimand_frozen",
                "immutable_scorer_frozen",
                "prospective_holdout_frozen",
            )
        ),
        [packet["candidate_neutral_estimand_frozen"], packet["immutable_scorer_frozen"], packet["prospective_holdout_frozen"]],
        [False, False, False],
    )
    check("packet is not synthetic", packet["synthetic"] is False and packet["source_artifact"]["synthetic"] is False, [packet["synthetic"], packet["source_artifact"]["synthetic"]], [False, False])
    state = r471_production_state(packet, r471)
    expected_state = intake["test_oracles"]["expected_structural_state"]
    check("R-471 structural state", state == expected_state, state, expected_state)
    check("manifest structural state", packet["r471_structural_state"] == state, packet["r471_structural_state"], state)

    boundary = intake["admission_boundary"]
    check("one structural candidate", boundary["structurally_registered_candidate_count"] == 1, boundary["structurally_registered_candidate_count"], 1)
    check("finite model remains unaudited", boundary["finite_model_consistent"] is False, boundary["finite_model_consistent"], False)
    check("physical owner not admitted", boundary["physical_owner_admitted"] is False, boundary["physical_owner_admitted"], False)
    check("physical projection not admitted", boundary["physical_projection_admitted"] is False, boundary["physical_projection_admitted"], False)
    check("scoring not admitted", boundary["scoring_admitted"] is False, boundary["scoring_admitted"], False)
    check("prospective validation absent", boundary["prospective_validated"] is False, boundary["prospective_validated"], False)
    check("no gate transition", boundary["gate_changed"] is False and boundary["scientific_transition"] is False, [boundary["gate_changed"], boundary["scientific_transition"]], [False, False])

    interpretation = source["interpretive_boundary"]
    check("event horizon identity locked", interpretation["event_horizon_identity"] == "NOT_CLAIMED", interpretation["event_horizon_identity"], "NOT_CLAIMED")
    check("Pre-A identity locked", interpretation["pre_a_identity"] == "NOT_CLAIMED", interpretation["pre_a_identity"], "NOT_CLAIMED")
    check("black-hole identity excluded", interpretation["not_a_black_hole_interior_model"] is True, interpretation["not_a_black_hole_interior_model"], True)

    uniform = source["common_core_and_uniform_contract"]
    check("common core declared", isinstance(uniform["common_core"], str) and bool(uniform["common_core"].strip()), uniform["common_core"], "nonempty")
    check("common norm declared", isinstance(uniform["common_norm"], str) and bool(uniform["common_norm"].strip()), uniform["common_norm"], "nonempty")
    check("uniform constant and range declared", isinstance(uniform["uniform_constant"], str) and bool(uniform["uniform_constant"].strip()) and len(uniform["independence_set"]) > 0, [uniform["uniform_constant"], uniform["independence_set"]], "nonempty")
    check("continuum estimate remains false", uniform["continuum_uniform_estimate"] is False, uniform["continuum_uniform_estimate"], False)
    limits = source["ordered_limits"]
    limit_ids = [item["id"] for item in limits["order"]]
    check("limit ids unique", len(limit_ids) == len(set(limit_ids)) and bool(limit_ids), limit_ids, "nonempty unique order")
    check("no limit interchange", limits["interchange_claimed"] is False, limits["interchange_claimed"], False)
    check("critical limit order", limit_ids.index("APERTURE_COLLAPSE") < limit_ids.index("OBSERVATION_TIME"), limit_ids, "APERTURE_COLLAPSE before OBSERVATION_TIME")
    check("assumptions declared", bool(source["assumptions"]) and bool(source["missing_assumptions"]), [len(source["assumptions"]), len(source["missing_assumptions"])], "both nonempty")
    check("falsifiers declared", bool(source["falsifiers"]) and all(item.get("id") and item.get("failure") for item in source["falsifiers"]), len(source["falsifiers"]), "nonempty identified falsifiers")
    check("nonclaims declared", bool(source["non_claims"]) and any("event horizon" in text.lower() for text in source["non_claims"]), len(source["non_claims"]), "explicit event-horizon nonclaim")

    core = core_record(intake, source, r471, state, intake_hash, source_hash, r471_hash)
    core_digest = canonical_digest(core)
    minimum = int(intake["test_oracles"]["primary_minimum_assertions"])
    check("primary assertion floor", len(checks) + 1 >= minimum, len(checks) + 1, f">={minimum}")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PAH-001-STRUCTURAL-INTAKE-PRIMARY",
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
        "structurally_registered_candidate_count": boundary["structurally_registered_candidate_count"],
        "physical_owner_admitted": False,
        "physical_projection_admitted": False,
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "core": core,
        "core_digest": core_digest,
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "evidence_level": "T0 / HASH-PINNED RESEARCHER-HYPOTHESIS STRUCTURAL INTAKE",
        "boundary": intake["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "intake_sha256": intake_hash,
            "source_sha256": source_hash,
            "authority_sha256": authority_hashes,
        },
    }
    if output is not None:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(
        f"PAH001 INTAKE PRIMARY PASS {len(checks)}/{len(checks)}; "
        f"state={state}; production=NONE; core={core_digest}"
    )
    return payload


def main() -> int:
    intake = load_json(INTAKE)
    default_output = repo_path(intake["runs"]["primary"])
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--no-store", action="store_true")
    arguments = parser.parse_args()
    run(None if arguments.no_store else arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
