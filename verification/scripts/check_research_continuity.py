#!/usr/bin/env python3
"""Validate the persistent dual-lane TECT research-continuity contract.

Ordinary mode validates only stable, commit-time-safe structure. The explicit
--strict-baseline mode additionally audits the post-commit/post-push baseline;
it must never be placed in gates.py.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
__first_issued__ = "2026-08-30"
__version_issued__ = "2026-08-30"

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "main-proof-program-v1.json"
GATES_SCRIPT = REPO / "verification" / "scripts" / "gates.py"

EXPECTED_SCHEMA = "tect/main-proof-program/1.0"
EXPECTED_PROGRAMME_ID = "TECT-PRE-A-SECTOR-A-MAIN-PROOF-PROGRAM-v1"
EXPECTED_PHASES = ["P0R", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]
EXPECTED_LAYERS = [
    "L1_MATHEMATICAL_THEOREM",
    "L2_MODEL_CONSISTENCY",
    "L3_PHYSICAL_IDENTITY",
    "L4_EMPIRICAL_VALIDATION",
]
EXPECTED_EVIDENCE_AXES = {
    "limit_scope": {"FINITE", "UNIFORM", "ORDERED_LIMIT"},
    "physical_scope": {"AUXILIARY", "MODEL", "IDENTIFIED"},
    "data_role": {"THEORY", "CALIBRATION", "RETROSPECTIVE", "PROSPECTIVE"},
}
EXPECTED_LANE_TASKS = {"forward": "T-054", "inverse": "T-059"}
EXPECTED_LANE_GATES = {
    "forward": "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
    "inverse": "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE",
}
EXPECTED_PHASE_ZERO_GATE = "RESEARCH-CONTINUITY-P0-BASELINE-AND-RESUME"
EXPECTED_TASK_IDS = {"T-054", "T-059", "T-060", "T-061"}
EXPECTED_GATE_IDS = {
    EXPECTED_PHASE_ZERO_GATE,
    EXPECTED_LANE_GATES["forward"],
    EXPECTED_LANE_GATES["inverse"],
}
EXPECTED_SYNCHRONIZATION_GATES = {
    "X1_NO_CIRCULARITY_COMPATIBILITY",
    "X2_GATE_SYNTHESIS",
    "X3_CLAIM_ACTION",
}
EXPECTED_STOPPED_LOOPS = {
    "PHYSICAL-EMPTY-COMMON-PARENT-AND-E-MISSING",
    "A13-COMPLETE-OWNER-PACKET-MISSING",
    "Q3LOCK-FINITE-TABLE-WITHOUT-UNIFORM-TRANSFER",
    "STATIC-TO-DYNAMICS-NONIDENTIFIABILITY",
    "GENERIC-OWNER-SEARCH-WITHOUT-NEW-HASH",
}
EXPECTED_METHOD_PRESERVATION = {
    "existing_forward_methods_unchanged",
    "inverse_lane_additive_not_replacement",
    "phases_are_resume_index_not_new_proof_method",
    "existing_authorities_remain_controlling",
}
EXPECTED_TRUE_FIREWALL_FLAGS = {
    "finite_does_not_imply_uniform",
    "finite_does_not_imply_continuum",
    "model_consistency_does_not_imply_physical_identity",
    "physical_identity_does_not_imply_empirical_validation",
    "retrospective_is_not_prospective",
    "post_unseal_retuning_forbidden",
    "cross_lane_circular_support_forbidden",
    "reference_only_no_matrix_copy",
}
EXPECTED_FALSE_FIREWALL_FLAGS = {"external_reference_claim_bearing"}
EXPECTED_CHECKPOINT_FIELDS = {
    "programme_version",
    "lane",
    "phase",
    "candidate_version",
    "exact_question",
    "exact_scope",
    "functional_or_action",
    "generator_or_transfer",
    "state",
    "physical_projection",
    "physical_owner",
    "proof_owner",
    "assumptions",
    "missing_assumptions",
    "regulator",
    "volume",
    "boundary_condition",
    "reference",
    "normalization",
    "finite_parts",
    "common_norm",
    "limit_order",
    "evidence_layer",
    "limit_scope",
    "physical_scope",
    "data_role",
    "reproduction",
    "artefacts_and_hashes",
    "primary_disposition",
    "independent_disposition",
    "hostile_disposition",
    "lean_disposition",
    "acceptance",
    "falsifier",
    "stop_or_redesign",
    "allowed_claims",
    "non_claims",
    "ledger_pointers",
    "next_action",
    "resume_condition",
}
EXPECTED_STATES = {
    "UNSTARTED",
    "READY",
    "ACTIVE",
    "CHECKPOINTED",
    "BLOCKED",
    "PARKED",
    "REDESIGN_REQUIRED",
    "COMPLETE",
}
EXPECTED_TRANSITIONS = {
    "UNSTARTED": {"READY"},
    "READY": {"ACTIVE", "PARKED"},
    "ACTIVE": {"CHECKPOINTED", "BLOCKED", "PARKED", "REDESIGN_REQUIRED"},
    "CHECKPOINTED": {"ACTIVE", "COMPLETE", "REDESIGN_REQUIRED"},
    "BLOCKED": {"ACTIVE", "PARKED", "REDESIGN_REQUIRED"},
    "PARKED": {"READY"},
    "REDESIGN_REQUIRED": {"READY"},
    "COMPLETE": set(),
}
EXPECTED_COUNT_KEYS = {
    "claims",
    "gates_and_hypotheses",
    "results",
    "negative_records",
    "explorations",
    "changelog_events",
    "tasks",
}
EXPECTED_WORK_PACKET_FIELDS = {
    "id",
    "status",
    "exact_question",
    "forward_scope",
    "inverse_scope",
    "starting_facts",
    "deliverables",
    "acceptance",
    "falsifiers",
    "stop_or_redesign",
    "evidence_layer",
    "limit_scope",
    "physical_scope",
    "data_roles",
    "non_claims",
    "next_action",
}
HOSTILE_TEST_MINIMUM = 10  # Tooling threshold, not a research-derived value.
COMMAND_TIMEOUT_SECONDS = 900  # Tooling timeout, not a research-derived value.
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FINGERPRINT_RE = re.compile(r"^[A-Z0-9][A-Z0-9-]{7,}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(raw: object) -> Path | None:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute():
        return None
    candidate = (REPO / raw).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return None
    return candidate


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True).lower()


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def recursive_strings(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.add(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key))
            found.update(recursive_strings(child))
    elif isinstance(value, list):
        for child in value:
            found.update(recursive_strings(child))
    return found


def semantic_strings(path: Path) -> set[str]:
    if path.suffix.lower() in {".json", ".jsonl"}:
        if path.suffix.lower() == ".json":
            return recursive_strings(load_json(path))
        values: set[str] = set()
        for line_number, raw in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if raw.strip():
                try:
                    values.update(recursive_strings(json.loads(raw)))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: {exc}") from exc
        return values
    return {path.read_text(encoding="utf-8")}


def registered_task_map() -> dict[str, dict[str, Any]]:
    payload = load_json(REPO / "todo" / "todo.json")
    return {
        str(item.get("id")): item
        for item in payload.get("tasks", [])
        if isinstance(item, dict) and item.get("id")
    }


def registered_gate_ids() -> set[str]:
    payload = load_json(REPO / "claims" / "gates-index.json")
    return {
        str(item.get("id"))
        for item in payload.get("entries", [])
        if isinstance(item, dict) and item.get("id")
    }


def validate_gate_registration() -> list[str]:
    errors: list[str] = []
    try:
        namespace = runpy.run_path(str(GATES_SCRIPT))
    except (OSError, SyntaxError, RuntimeError) as exc:
        return [f"cannot inspect gates.py: {exc}"]
    entries = namespace.get("SYNC_GATES")
    if not isinstance(entries, list):
        return ["gates.py lacks a SYNC_GATES list"]
    matches = [
        entry
        for entry in entries
        if isinstance(entry, (list, tuple))
        and len(entry) == 2
        and entry[0] == "research-continuity"
    ]
    if len(matches) != 1:
        errors.append("gates.py must contain exactly one research-continuity gate")
    elif matches[0][1] != ["check_research_continuity.py"]:
        errors.append(
            "research-continuity gate must be ordinary mode only; "
            "--strict-baseline is forbidden in gates.py"
        )
    return errors


def validate_authority_pointers(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pointers = data.get("authority_pointers")
    if not isinstance(pointers, dict):
        return ["authority_pointers must be an object"]

    immutable = pointers.get("immutable")
    if not isinstance(immutable, list) or not immutable:
        errors.append("authority_pointers.immutable must be a nonempty list")
        immutable = []
    immutable_paths: set[str] = set()
    for pointer in immutable:
        if not isinstance(pointer, dict) or set(pointer) != {
            "path",
            "sha256",
            "role",
        }:
            errors.append(f"malformed immutable authority pointer: {pointer!r}")
            continue
        raw_path = pointer["path"]
        path = repo_path(raw_path)
        if path is None:
            errors.append(f"unsafe immutable pointer path: {raw_path!r}")
            continue
        if str(raw_path) in immutable_paths:
            errors.append(f"duplicate immutable pointer: {raw_path}")
        immutable_paths.add(str(raw_path))
        expected = pointer["sha256"]
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            errors.append(f"{raw_path}: malformed sha256")
        if not nonempty(pointer["role"]):
            errors.append(f"{raw_path}: pointer role missing")
        if not path.is_file():
            errors.append(f"{raw_path}: immutable authority missing")
        elif isinstance(expected, str) and SHA256_RE.fullmatch(expected):
            if sha256(path) != expected:
                errors.append(f"{raw_path}: immutable authority hash drift")

    semantic = pointers.get("semantic")
    if not isinstance(semantic, list) or not semantic:
        errors.append("authority_pointers.semantic must be a nonempty list")
        semantic = []
    semantic_paths: set[str] = set()
    required_semantic_ids: set[str] = set()
    for pointer in semantic:
        if not isinstance(pointer, dict) or set(pointer) != {
            "path",
            "role",
            "required_ids",
            "freshness",
        }:
            errors.append(f"malformed semantic authority pointer: {pointer!r}")
            continue
        raw_path = pointer["path"]
        path = repo_path(raw_path)
        if path is None:
            errors.append(f"unsafe semantic pointer path: {raw_path!r}")
            continue
        if str(raw_path) in semantic_paths:
            errors.append(f"duplicate semantic pointer: {raw_path}")
        semantic_paths.add(str(raw_path))
        required_ids = pointer["required_ids"]
        if not isinstance(required_ids, list) or any(
            not isinstance(item, str) or not item for item in required_ids
        ):
            errors.append(f"{raw_path}: required_ids must be a string list")
            required_ids = []
        required_semantic_ids.update(required_ids)
        if not nonempty(pointer["role"]) or not nonempty(pointer["freshness"]):
            errors.append(f"{raw_path}: semantic role/freshness missing")
        if not path.is_file():
            errors.append(f"{raw_path}: semantic authority missing")
            continue
        try:
            values = semantic_strings(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{raw_path}: cannot read semantic authority: {exc}")
            continue
        if path.suffix.lower() in {".md", ".txt"}:
            text = next(iter(values), "")
            missing = [item for item in required_ids if item not in text]
        else:
            missing = [item for item in required_ids if item not in values]
        for item in missing:
            errors.append(f"{raw_path}: required semantic id missing: {item}")

    if not EXPECTED_TASK_IDS <= required_semantic_ids:
        errors.append(
            "semantic pointers must preserve T-054/T-059/T-060/T-061 task IDs"
        )
    if not EXPECTED_GATE_IDS <= required_semantic_ids:
        errors.append("semantic pointers must preserve the three active gate IDs")
    return errors


def validate_state_machine(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    machine = data.get("state_machine")
    if not isinstance(machine, dict):
        return ["state_machine must be an object"]
    states = machine.get("states")
    if not isinstance(states, list) or set(states) != EXPECTED_STATES:
        errors.append("state_machine.states drifted")
    transitions = machine.get("allowed_transitions")
    normalized: dict[str, set[str]] = {}
    if not isinstance(transitions, dict):
        errors.append("state_machine.allowed_transitions must be an object")
    else:
        normalized = {
            str(source): set(targets) if isinstance(targets, list) else set()
            for source, targets in transitions.items()
        }
        if normalized != EXPECTED_TRANSITIONS:
            errors.append("state_machine.allowed_transitions drifted")
    repeated = str(machine.get("repeated_blocker_rule", "")).lower()
    for token in ("fingerprint", "new hash-pinned input", "parked", "blocked"):
        if token not in repeated:
            errors.append(f"repeated-blocker rule lacks {token!r}")
    if "BLOCKED" in normalized.get("BLOCKED", set()):
        errors.append("BLOCKED -> BLOCKED repetition must never be allowed")
    return errors


def validate_phase_graph(data: dict[str, Any]) -> tuple[list[str], dict[str, dict]]:
    errors: list[str] = []
    phases = data.get("research_phases")
    if not isinstance(phases, list):
        return ["research_phases must be a list"], {}
    phase_fields = {
        "id",
        "title",
        "predecessors",
        "forward_method",
        "inverse_method",
        "exit_gate",
        "required_records",
        "stop_or_redesign",
    }
    ids = [item.get("id") for item in phases if isinstance(item, dict)]
    if ids != EXPECTED_PHASES:
        errors.append(f"phase order must be {' -> '.join(EXPECTED_PHASES)}")
    phase_map: dict[str, dict] = {}
    exit_gates: set[str] = set()
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict) or set(phase) != phase_fields:
            errors.append(f"phase {index}: malformed fields")
            continue
        phase_id = str(phase["id"])
        if phase_id in phase_map:
            errors.append(f"duplicate phase id: {phase_id}")
        phase_map[phase_id] = phase
        expected_predecessors = [] if index == 0 else [EXPECTED_PHASES[index - 1]]
        if phase["predecessors"] != expected_predecessors:
            errors.append(f"{phase_id}: predecessor chain drift")
        for field in (
            "title",
            "forward_method",
            "inverse_method",
            "exit_gate",
            "stop_or_redesign",
        ):
            if not nonempty(phase[field]):
                errors.append(f"{phase_id}: {field} missing")
        if not isinstance(phase["required_records"], list) or not phase[
            "required_records"
        ]:
            errors.append(f"{phase_id}: required_records missing")
        exit_gate = str(phase["exit_gate"])
        if exit_gate in exit_gates:
            errors.append(f"duplicate phase exit gate: {exit_gate}")
        exit_gates.add(exit_gate)

    if phase_map.get("P0R", {}).get("exit_gate") != EXPECTED_PHASE_ZERO_GATE:
        errors.append("P0R must exit through the continuity baseline gate")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(phase_id: str) -> None:
        if phase_id in visiting:
            errors.append(f"phase graph cycle at {phase_id}")
            return
        if phase_id in visited or phase_id not in phase_map:
            return
        visiting.add(phase_id)
        for predecessor in phase_map[phase_id].get("predecessors", []):
            if predecessor not in phase_map:
                errors.append(f"{phase_id}: unknown predecessor {predecessor}")
            else:
                visit(predecessor)
        visiting.remove(phase_id)
        visited.add(phase_id)

    for phase_id in phase_map:
        visit(phase_id)
    return errors, phase_map


def validate_lanes(data: dict[str, Any], phase_map: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    lanes = data.get("lanes")
    if not isinstance(lanes, dict) or set(lanes) != {"forward", "inverse"}:
        return ["lanes must contain exactly forward and inverse"]
    live_tasks = registered_task_map()
    live_gates = registered_gate_ids()

    for lane_id in ("forward", "inverse"):
        lane = lanes[lane_id]
        if not isinstance(lane, dict):
            errors.append(f"{lane_id}: lane must be an object")
            continue
        if lane.get("task_id") != EXPECTED_LANE_TASKS[lane_id]:
            errors.append(f"{lane_id}: wrong task owner")
        if lane.get("science_gate") != EXPECTED_LANE_GATES[lane_id]:
            errors.append(f"{lane_id}: wrong science gate")
        task = live_tasks.get(str(lane.get("task_id")))
        if task is None:
            errors.append(f"{lane_id}: live task missing")
        elif task.get("gate") != lane.get("science_gate"):
            errors.append(f"{lane_id}: live task/science-gate mismatch")
        if lane.get("science_gate") not in live_gates:
            errors.append(f"{lane_id}: science gate is not registered")

        states = lane.get("stage_states")
        if not isinstance(states, dict) or set(states) != set(EXPECTED_PHASES):
            errors.append(f"{lane_id}: stage_states must cover every phase exactly")
            continue
        invalid = {
            phase_id: state
            for phase_id, state in states.items()
            if state not in EXPECTED_STATES
        }
        if invalid:
            errors.append(f"{lane_id}: invalid stage state(s): {invalid}")
        active = [phase_id for phase_id, state in states.items() if state == "ACTIVE"]
        if len(active) != 1:
            errors.append(f"{lane_id}: exactly one ACTIVE stage is required")
        elif lane.get("current_stage") != active[0]:
            errors.append(f"{lane_id}: current_stage does not name its ACTIVE stage")

        for phase_id, state in states.items():
            if state not in {"ACTIVE", "CHECKPOINTED", "COMPLETE"}:
                continue
            for predecessor in phase_map.get(phase_id, {}).get("predecessors", []):
                if states.get(predecessor) != "COMPLETE":
                    if state == "COMPLETE" or phase_id == lane.get("current_stage"):
                        errors.append(
                            f"{lane_id}:{phase_id}: predecessor {predecessor} "
                            "is not COMPLETE"
                        )

        if not nonempty(lane.get("scientific_frontier")):
            errors.append(f"{lane_id}: scientific_frontier missing")
        if not nonempty(lane.get("next_gate_after_p0r")):
            errors.append(f"{lane_id}: next action after P0R missing")

    current_phase = data.get("current_phase")
    active_union = {
        lane.get("current_stage")
        for lane in lanes.values()
        if isinstance(lane, dict)
    }
    if current_phase not in active_union:
        errors.append("current_phase is not active in either lane")
    if data.get("status") == "RECOVERY_IN_PROGRESS":
        if any(
            lane.get("current_stage") != "P0R"
            for lane in lanes.values()
            if isinstance(lane, dict)
        ):
            errors.append("RECOVERY_IN_PROGRESS requires both lanes at P0R")
    return errors


def validate_recovery_snapshot(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    snapshot = data.get("recovery_start_snapshot")
    if not isinstance(snapshot, dict):
        return ["recovery_start_snapshot must be an object"]
    for field in (
        "branch",
        "head",
        "ahead",
        "behind",
        "staged_paths",
        "unstaged_tracked_paths",
        "untracked_paths",
        "pending_paths_total",
        "commit_queue_pending",
        "doctor",
        "release_check",
        "authority_counts",
        "authority_state",
    ):
        if field not in snapshot:
            errors.append(f"recovery_start_snapshot lacks {field}")
    if not COMMIT_RE.fullmatch(str(snapshot.get("head", ""))):
        errors.append("recovery-start HEAD is malformed")
    for field in (
        "ahead",
        "behind",
        "staged_paths",
        "unstaged_tracked_paths",
        "untracked_paths",
        "pending_paths_total",
        "commit_queue_pending",
    ):
        value = snapshot.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"recovery-start {field} must be a nonnegative integer")
    components = [
        snapshot.get("staged_paths"),
        snapshot.get("unstaged_tracked_paths"),
        snapshot.get("untracked_paths"),
    ]
    if all(isinstance(value, int) for value in components):
        if snapshot.get("pending_paths_total") != sum(components):
            errors.append("recovery-start pending path total is inconsistent")
    counts = snapshot.get("authority_counts")
    if not isinstance(counts, dict) or set(counts) != EXPECTED_COUNT_KEYS:
        errors.append("recovery-start authority count keys drifted")
    elif any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in counts.values()
    ):
        errors.append("recovery-start authority counts must be nonnegative integers")
    if snapshot.get("release_check") == "PASS":
        non_claims = json_text(data.get("non_claims"))
        if "does not mean" not in non_claims or "committed or pushed" not in non_claims:
            errors.append("release PASS durability non-claim is missing")
    return errors


def validate_completion_checkpoint(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checkpoint = data.get("completion_checkpoint")
    required = {
        "status",
        "verified_parent_head",
        "verified_at_utc",
        "branch",
        "remote",
        "remote_ref",
        "expected_authority_counts",
        "requirements",
        "evidence",
    }
    if not isinstance(checkpoint, dict) or set(checkpoint) != required:
        return ["completion_checkpoint fields are malformed"]
    status = checkpoint.get("status")
    if status not in {"PENDING", "COMPLETE"}:
        errors.append("completion checkpoint status must be PENDING or COMPLETE")
    if checkpoint.get("branch") != "main":
        errors.append("completion checkpoint branch must remain main")
    if checkpoint.get("remote_ref") != "refs/heads/main":
        errors.append("completion checkpoint remote_ref must remain refs/heads/main")
    if not nonempty(checkpoint.get("remote")):
        errors.append("completion checkpoint remote missing")
    if not isinstance(checkpoint.get("requirements"), list) or not checkpoint[
        "requirements"
    ]:
        errors.append("completion checkpoint requirements missing")
    if not isinstance(checkpoint.get("evidence"), list):
        errors.append("completion checkpoint evidence must be a list")
    counts = checkpoint.get("expected_authority_counts")
    if status == "PENDING":
        if counts is not None:
            errors.append("PENDING completion checkpoint must not freeze counts")
    else:
        if not isinstance(counts, dict) or set(counts) != EXPECTED_COUNT_KEYS:
            errors.append("COMPLETE checkpoint authority count keys drifted")
        elif any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in counts.values()
        ):
            errors.append("COMPLETE checkpoint counts must be nonnegative integers")
        if not COMMIT_RE.fullmatch(str(checkpoint.get("verified_parent_head", ""))):
            errors.append("verified_parent_head must be a 40-hex provenance commit")
        if not nonempty(checkpoint.get("verified_at_utc")):
            errors.append("COMPLETE checkpoint lacks verified_at_utc")
        if not checkpoint.get("evidence"):
            errors.append("COMPLETE checkpoint lacks evidence")
    return errors


def validate_stopped_loops(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    registry = data.get("stopped_loop_registry")
    required = {
        "fingerprint",
        "status",
        "evidence",
        "reopen_condition",
        "forbidden_repeat",
    }
    if not isinstance(registry, list) or not registry:
        return ["stopped_loop_registry must be a nonempty list"]
    fingerprints: list[str] = []
    for item in registry:
        if not isinstance(item, dict) or set(item) != required:
            errors.append(f"malformed stopped-loop record: {item!r}")
            continue
        fingerprint = str(item["fingerprint"])
        fingerprints.append(fingerprint)
        if not FINGERPRINT_RE.fullmatch(fingerprint):
            errors.append(f"malformed stopped-loop fingerprint: {fingerprint}")
        if item["status"] not in {"PARKED", "REDESIGN_REQUIRED"}:
            errors.append(f"{fingerprint}: repeated blocker cannot remain BLOCKED")
        if not isinstance(item["evidence"], list) or not item["evidence"]:
            errors.append(f"{fingerprint}: evidence missing")
        if not nonempty(item["reopen_condition"]):
            errors.append(f"{fingerprint}: reopen condition missing")
        forbidden = str(item["forbidden_repeat"]).lower()
        if "do not" not in forbidden:
            errors.append(f"{fingerprint}: explicit forbidden repeat missing")
    if len(fingerprints) != len(set(fingerprints)):
        errors.append("duplicate stopped-loop fingerprint")
    if not EXPECTED_STOPPED_LOOPS <= set(fingerprints):
        errors.append("one or more established stopped-loop fingerprints disappeared")
    return errors


def validate_work_packet(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    packet = data.get("current_work_packet")
    if not isinstance(packet, dict):
        return ["current_work_packet must be an object"]
    missing = EXPECTED_WORK_PACKET_FIELDS - set(packet)
    if missing:
        errors.append(f"current_work_packet missing fields: {sorted(missing)}")
    for field in (
        "id",
        "status",
        "exact_question",
        "forward_scope",
        "inverse_scope",
        "acceptance",
        "stop_or_redesign",
        "evidence_layer",
        "limit_scope",
        "physical_scope",
        "next_action",
    ):
        if not nonempty(packet.get(field)):
            errors.append(f"current_work_packet.{field} is empty")
    for field in (
        "starting_facts",
        "deliverables",
        "falsifiers",
        "data_roles",
        "non_claims",
    ):
        if not isinstance(packet.get(field), list) or not packet.get(field):
            errors.append(f"current_work_packet.{field} must be a nonempty list")
    roles = set(packet.get("data_roles", []))
    if not roles <= EXPECTED_EVIDENCE_AXES["data_role"]:
        errors.append("current work packet contains an invalid data role")
    if packet.get("evidence_layer") not in set(EXPECTED_LAYERS):
        errors.append("current work packet evidence layer is invalid")
    if packet.get("limit_scope") not in EXPECTED_EVIDENCE_AXES["limit_scope"]:
        errors.append("current work packet limit scope is invalid")
    if packet.get("physical_scope") not in EXPECTED_EVIDENCE_AXES["physical_scope"]:
        errors.append("current work packet physical scope is invalid")
    if data.get("current_phase") == "P0R":
        if packet.get("status") != "READY_WAITING_P0R":
            errors.append("P0R successor packet must remain READY_WAITING_P0R")
        if "T-061" not in str(packet.get("next_action", "")):
            errors.append("P0R successor packet must identify T-061")
    return errors


def validate_resume_algorithm(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    algorithm = data.get("resume_algorithm")
    if not isinstance(algorithm, list) or len(algorithm) < 8:
        return ["resume_algorithm must contain the ordered restart procedure"]
    lowered = [str(step).lower() for step in algorithm]

    predicates = [
        lambda text: "utc" in text and "doctor" in text,
        lambda text: "check_research_continuity.py" in text,
        lambda text: "management/index.md" in text and "task" in text,
        lambda text: "programme" in text and "exploration" in text,
        lambda text: "hash" in text and "semantic" in text,
        lambda text: "p0r" in text and "drift" in text,
        lambda text: "active phase" in text,
    ]
    positions: list[int] = []
    for predicate in predicates:
        match = next(
            (index for index, step in enumerate(lowered) if predicate(step)), None
        )
        if match is None:
            errors.append("resume_algorithm is missing a required ordered step")
        else:
            positions.append(match)
    if len(positions) == len(predicates) and positions != sorted(positions):
        errors.append("resume_algorithm step order drifted")
    combined = " ".join(lowered)
    if "chat" not in combined or not any(
        phrase in combined
        for phrase in ("not authority", "context only", "never the resume authority")
    ):
        errors.append("resume_algorithm must state that chat is not resume authority")
    return errors


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"schema must be {EXPECTED_SCHEMA}")
    if data.get("id") != EXPECTED_PROGRAMME_ID:
        errors.append("programme id drifted")
    if data.get("version") != "1.0.0":
        errors.append("programme version drifted")
    if not DATE_RE.fullmatch(str(data.get("recorded_on", ""))):
        errors.append("recorded_on must be an ISO date")
    if data.get("claim_bearing") is not False or data.get("tier") != "T0":
        errors.append("continuity overlay must remain non-claim-bearing T0")
    if not nonempty(data.get("authority")) or not nonempty(data.get("objective")):
        errors.append("authority/objective missing")
    if data.get("phase_zero_gate") != EXPECTED_PHASE_ZERO_GATE:
        errors.append("phase-zero gate drifted")

    preservation = data.get("method_preservation")
    if not isinstance(preservation, dict):
        errors.append("method_preservation must be an object")
    else:
        for flag in EXPECTED_METHOD_PRESERVATION:
            if preservation.get(flag) is not True:
                errors.append(f"method-preservation firewall false: {flag}")
        conflict = str(preservation.get("conflict_rule", "")).lower()
        if (
            "issued authority controls" not in conflict
            or "p0r" not in conflict
            or "correction" not in conflict
        ):
            errors.append("method-preservation conflict rule is incomplete")

    errors.extend(validate_authority_pointers(data))

    layers = data.get("layer_contract")
    layer_ids = (
        [item.get("id") for item in layers if isinstance(item, dict)]
        if isinstance(layers, list)
        else []
    )
    if layer_ids != EXPECTED_LAYERS:
        errors.append("four-layer contract order or identity drifted")
    if isinstance(layers, list):
        for layer in layers:
            if not isinstance(layer, dict) or set(layer) != {
                "id",
                "question",
                "promotion_boundary",
            }:
                errors.append("malformed layer-contract entry")
            elif not nonempty(layer["question"]) or not nonempty(
                layer["promotion_boundary"]
            ):
                errors.append(f"{layer.get('id')}: layer question/boundary missing")

    axes = data.get("evidence_axes")
    if not isinstance(axes, dict):
        errors.append("evidence_axes must be an object")
    else:
        for axis, expected in EXPECTED_EVIDENCE_AXES.items():
            values = axes.get(axis)
            if not isinstance(values, list) or set(values) != expected:
                errors.append(f"evidence axis drift: {axis}")
        if axes.get("no_automatic_promotion") is not True:
            errors.append("evidence axes must forbid automatic promotion")

    checkpoint_fields = data.get("checkpoint_required_fields")
    if not isinstance(checkpoint_fields, list) or not EXPECTED_CHECKPOINT_FIELDS <= set(
        checkpoint_fields
    ):
        errors.append("checkpoint required-field contract is incomplete")

    errors.extend(validate_state_machine(data))
    phase_errors, phase_map = validate_phase_graph(data)
    errors.extend(phase_errors)

    synchronization = data.get("synchronization_gates")
    if not isinstance(synchronization, list):
        errors.append("synchronization_gates must be a list")
    else:
        synchronization_ids = {
            item.get("id") for item in synchronization if isinstance(item, dict)
        }
        if synchronization_ids != EXPECTED_SYNCHRONIZATION_GATES:
            errors.append("synchronization-gate set drifted")
        for item in synchronization:
            if not isinstance(item, dict) or set(item) != {"id", "rule"}:
                errors.append("malformed synchronization gate")
            elif not nonempty(item["rule"]):
                errors.append(f"{item.get('id')}: synchronization rule missing")

    errors.extend(validate_lanes(data, phase_map))
    errors.extend(validate_recovery_snapshot(data))
    errors.extend(validate_completion_checkpoint(data))
    errors.extend(validate_stopped_loops(data))
    errors.extend(validate_work_packet(data))
    errors.extend(validate_resume_algorithm(data))

    flags = data.get("firewall_flags")
    if not isinstance(flags, dict):
        errors.append("firewall_flags must be an object")
    else:
        for flag in EXPECTED_TRUE_FIREWALL_FLAGS:
            if flags.get(flag) is not True:
                errors.append(f"required firewall false: {flag}")
        for flag in EXPECTED_FALSE_FIREWALL_FLAGS:
            if flags.get(flag) is not False:
                errors.append(f"required false firewall changed: {flag}")

    firewalls = data.get("firewalls")
    required_firewall_ids = {
        "NO_MATRIX_COPY",
        "NO_LAYER_PROMOTION",
        "NO_RETROSPECTIVE_AS_PROSPECTIVE",
        "NO_MISSING_MAP_PASS",
        "NO_CIRCULAR_LANE_PROOF",
        "NO_REFERENCE_ONLY_PROMOTION",
        "NO_POST_UNSEAL_TUNING",
        "NO_REPEATED_BLOCKER",
        "NO_A14_INFLATION",
    }
    firewall_ids = (
        {item.get("id") for item in firewalls if isinstance(item, dict)}
        if isinstance(firewalls, list)
        else set()
    )
    if firewall_ids != required_firewall_ids:
        errors.append("human-readable firewall set drifted")
    if isinstance(firewalls, list):
        for item in firewalls:
            if not isinstance(item, dict) or set(item) != {"id", "rule"}:
                errors.append("malformed human-readable firewall")

    all_keys = {string.lower() for string in recursive_strings(data)}
    if {"copied_matrix", "counterpart_matrix", "matrix_rows"} & all_keys:
        errors.append("copied counterpart matrix detected")

    non_claims = json_text(
        [
            data.get("non_claims"),
            data.get("current_work_packet", {}).get("non_claims"),
        ]
    )
    for token in (
        "pre-a",
        "c6",
        "a13",
        "sector a",
        "qft",
        "yang-mills",
        "gravity",
        "mass gap",
        "continuum",
    ):
        if token not in non_claims:
            errors.append(f"non-claim firewall missing {token}")

    try:
        live_tasks = registered_task_map()
        live_gates = registered_gate_ids()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read live task/gate authority: {exc}")
    else:
        for task_id in EXPECTED_TASK_IDS:
            if task_id not in live_tasks:
                errors.append(f"required live task missing: {task_id}")
        for gate_id in EXPECTED_GATE_IDS:
            if gate_id not in live_gates:
                errors.append(f"required live gate missing: {gate_id}")

    errors.extend(validate_gate_registration())
    return errors


def count_jsonl(path: Path) -> int:
    count = 0
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw.strip():
            continue
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        count += 1
    return count


def current_authority_counts() -> dict[str, int]:
    claim_count = 0
    for path in sorted((REPO / "claims").glob("*/status.json")):
        payload = load_json(path)
        if isinstance(payload, dict) and payload.get("id"):
            claim_count += 1
    gate_index = load_json(REPO / "claims" / "gates-index.json")
    result_index = load_json(REPO / "results" / "index.json")
    negative_index = load_json(REPO / "negative-results" / "index.json")
    todo = load_json(REPO / "todo" / "todo.json")
    return {
        "claims": claim_count,
        "gates_and_hypotheses": int(gate_index["count"]),
        "results": int(result_index["count"]),
        "negative_records": int(negative_index["count"]),
        "explorations": count_jsonl(REPO / "explorations" / "log.jsonl"),
        "changelog_events": count_jsonl(REPO / "changelog" / "log.jsonl"),
        "tasks": len(todo["tasks"]),
    }


def run_command(
    args: list[str], timeout: int = COMMAND_TIMEOUT_SECONDS
) -> tuple[int, str]:
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    try:
        process = subprocess.run(
            args,
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="strict",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    return process.returncode, process.stdout


def run_git(args: list[str], timeout: int = 60) -> tuple[int, str]:
    return run_command(["git", *args], timeout=timeout)


def queue_count() -> int:
    queue = REPO / "internal" / "commit-queue"
    if not queue.is_dir():
        return 0
    return sum(1 for path in queue.glob("*.json") if path.is_file())


def strict_observation_errors(
    checkpoint: dict[str, Any], observation: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if checkpoint.get("status") != "COMPLETE":
        errors.append("completion checkpoint is not COMPLETE")
    if observation.get("clean") is not True:
        errors.append("Git worktree is not clean")
    if observation.get("queue_count") != 0:
        errors.append("commit queue is not empty")
    if observation.get("branch") != checkpoint.get("branch"):
        errors.append("live branch differs from completion checkpoint")
    if observation.get("diff_check") is not True:
        errors.append("git diff --check failed")
    expected = checkpoint.get("expected_authority_counts")
    if observation.get("authority_counts") != expected:
        errors.append("live authority counts differ from completion checkpoint")
    if observation.get("doctor_pass") is not True:
        errors.append("doctor.py did not pass")
    if observation.get("release_pass") is not True:
        errors.append("release_check.py did not pass")
    if observation.get("remote_accessible") is not True:
        errors.append("live remote main could not be verified")
    elif observation.get("remote_head") != observation.get("local_head"):
        errors.append("live remote main differs from local HEAD")
    return errors


def strict_baseline(data: dict[str, Any]) -> int:
    ordinary_errors = validate(data)
    if ordinary_errors:
        print("RESEARCH-CONTINUITY STRICT: FAIL - ordinary contract invalid")
        for error in ordinary_errors:
            print(f"  - {error}")
        return 1

    checkpoint = data["completion_checkpoint"]
    status_code, porcelain = run_git(
        ["status", "--porcelain=v1", "--untracked-files=all"]
    )
    clean = status_code == 0 and not porcelain.strip()
    _, local_head_raw = run_git(["rev-parse", "HEAD"])
    _, branch_raw = run_git(["branch", "--show-current"])
    local_head = local_head_raw.strip()
    branch = branch_raw.strip()

    diff_work_code, _ = run_git(["diff", "--check"])
    diff_cached_code, _ = run_git(["diff", "--cached", "--check"])
    diff_check = diff_work_code == 0 and diff_cached_code == 0

    remote = str(checkpoint.get("remote", ""))
    remote_ref = str(checkpoint.get("remote_ref", ""))
    remote_code, remote_output = run_git(
        ["ls-remote", "--heads", remote, remote_ref], timeout=120
    )
    remote_accessible = remote_code == 0
    remote_head: str | None = None
    if remote_accessible and remote_output.strip():
        remote_head = remote_output.split()[0]
    elif remote_accessible:
        remote_accessible = False

    doctor_code, doctor_output = run_command(
        [sys.executable, "-X", "utf8", "verification/scripts/doctor.py"]
    )
    release_code, release_output = run_command(
        [sys.executable, "-X", "utf8", "verification/scripts/release_check.py"]
    )
    try:
        counts = current_authority_counts()
        count_error = None
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        counts = {}
        count_error = str(exc)

    observation = {
        "clean": clean,
        "queue_count": queue_count(),
        "local_head": local_head,
        "branch": branch,
        "diff_check": diff_check,
        "authority_counts": counts,
        "doctor_pass": doctor_code == 0,
        "release_pass": release_code == 0,
        "remote_accessible": remote_accessible,
        "remote_head": remote_head,
    }
    errors = strict_observation_errors(checkpoint, observation)
    if count_error:
        errors.append(f"cannot derive authority counts: {count_error}")
    if not COMMIT_RE.fullmatch(local_head):
        errors.append("cannot resolve local HEAD")
    if remote_accessible and not COMMIT_RE.fullmatch(str(remote_head or "")):
        errors.append("live remote returned no valid branch head")

    if errors:
        print("RESEARCH-CONTINUITY STRICT: FAIL")
        for error in errors:
            print(f"  - {error}")
        if doctor_code:
            print("  doctor tail:")
            for line in doctor_output.splitlines()[-8:]:
                print(f"    {line}")
        if release_code:
            print("  release tail:")
            for line in release_output.splitlines()[-8:]:
                print(f"    {line}")
        return 1

    print(
        "RESEARCH-CONTINUITY STRICT: PASS "
        f"(head={local_head}; remote={remote_head}; queue=0; clean=true; "
        f"counts={json.dumps(counts, sort_keys=True)})"
    )
    return 0


def self_test(data: dict[str, Any]) -> int:
    base_errors = validate(data)
    assert not base_errors, f"valid manifest rejected: {base_errors}"

    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str, change) -> None:
        candidate = copy.deepcopy(data)
        change(candidate)
        mutations.append((name, candidate))

    mutate("claim promotion", lambda item: item.__setitem__("claim_bearing", True))
    mutate(
        "method replacement",
        lambda item: item["method_preservation"].__setitem__(
            "inverse_lane_additive_not_replacement", False
        ),
    )
    mutate(
        "hash drift",
        lambda item: item["authority_pointers"]["immutable"][0].__setitem__(
            "sha256", "0" * 64
        ),
    )
    mutate(
        "semantic task loss",
        lambda item: item["authority_pointers"]["semantic"][2][
            "required_ids"
        ].append("T-NOT-REGISTERED"),
    )
    mutate("layer permutation", lambda item: item["layer_contract"].reverse())
    mutate(
        "transition shortcut",
        lambda item: item["state_machine"]["allowed_transitions"]["READY"].append(
            "COMPLETE"
        ),
    )
    mutate(
        "phase cycle",
        lambda item: item["research_phases"][0]["predecessors"].append("P7"),
    )
    mutate(
        "two active forward stages",
        lambda item: item["lanes"]["forward"]["stage_states"].__setitem__(
            "P1", "ACTIVE"
        ),
    )
    mutate(
        "successor complete before predecessor",
        lambda item: item["lanes"]["inverse"]["stage_states"].__setitem__(
            "P1", "COMPLETE"
        ),
    )
    mutate(
        "finite continuum promotion",
        lambda item: item["firewall_flags"].__setitem__(
            "finite_does_not_imply_continuum", False
        ),
    )
    mutate(
        "external claim promotion",
        lambda item: item["firewall_flags"].__setitem__(
            "external_reference_claim_bearing", True
        ),
    )
    mutate(
        "retrospective prospective conflation",
        lambda item: item["firewall_flags"].__setitem__(
            "retrospective_is_not_prospective", False
        ),
    )
    mutate(
        "repeated blocker",
        lambda item: item["stopped_loop_registry"][0].__setitem__(
            "status", "BLOCKED"
        ),
    )
    mutate(
        "duplicate blocker fingerprint",
        lambda item: item["stopped_loop_registry"][1].__setitem__(
            "fingerprint", item["stopped_loop_registry"][0]["fingerprint"]
        ),
    )
    mutate(
        "invalid data role",
        lambda item: item["current_work_packet"]["data_roles"].append(
            "FITTING_AS_PROSPECTIVE"
        ),
    )
    mutate("non-claim deletion", lambda item: item.__setitem__("non_claims", []))
    mutate(
        "missing checkpoint assumption field",
        lambda item: item["checkpoint_required_fields"].remove(
            "missing_assumptions"
        ),
    )
    mutate(
        "forward method deletion",
        lambda item: item["research_phases"][3].__setitem__("forward_method", ""),
    )

    rejected = 0
    for name, mutation in mutations:
        mutation_errors = validate(mutation)
        assert mutation_errors, f"hostile mutation accepted: {name}"
        rejected += 1

    fake_counts = {key: 0 for key in EXPECTED_COUNT_KEYS}
    fake_checkpoint = {
        "status": "COMPLETE",
        "branch": "main",
        "expected_authority_counts": fake_counts,
    }
    good_observation = {
        "clean": True,
        "queue_count": 0,
        "local_head": "a" * 40,
        "remote_head": "a" * 40,
        "remote_accessible": True,
        "branch": "main",
        "diff_check": True,
        "authority_counts": fake_counts,
        "doctor_pass": True,
        "release_pass": True,
    }
    assert not strict_observation_errors(fake_checkpoint, good_observation)

    strict_mutations = [
        ("dirty baseline", {"clean": False}),
        ("nonempty queue", {"queue_count": 1}),
        ("remote mismatch", {"remote_head": "b" * 40}),
        ("remote inaccessible", {"remote_accessible": False}),
        ("authority count mismatch", {"authority_counts": {**fake_counts, "tasks": 1}}),
    ]
    for name, patch in strict_mutations:
        observation = copy.deepcopy(good_observation)
        observation.update(patch)
        assert strict_observation_errors(
            fake_checkpoint, observation
        ), f"strict hostile mutation accepted: {name}"
        rejected += 1

    assert rejected >= HOSTILE_TEST_MINIMUM
    print(
        "RESEARCH-CONTINUITY SELFTEST: PASS "
        f"({rejected} hostile mutations rejected)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--strict-baseline",
        action="store_true",
        help="post-commit/post-push audit; forbidden in gates.py",
    )
    args = parser.parse_args()

    try:
        data = load_json(MANIFEST)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RESEARCH-CONTINUITY: FAIL - {exc}")
        return 1
    if not isinstance(data, dict):
        print("RESEARCH-CONTINUITY: FAIL - manifest root must be an object")
        return 1

    if args.self_test:
        return self_test(data)
    if args.strict_baseline:
        return strict_baseline(data)

    errors = validate(data)
    if errors:
        print("RESEARCH-CONTINUITY: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    immutable_count = len(data["authority_pointers"]["immutable"])
    semantic_count = len(data["authority_pointers"]["semantic"])
    stopped_count = len(data["stopped_loop_registry"])
    print(
        "RESEARCH-CONTINUITY: PASS "
        f"(phase={data['current_phase']}; lanes=2; phases={len(EXPECTED_PHASES)}; "
        f"immutable_pointers={immutable_count}; semantic_pointers={semantic_count}; "
        f"stopped_loops={stopped_count}; completion="
        f"{data['completion_checkpoint']['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
