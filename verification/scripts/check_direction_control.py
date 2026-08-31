#!/usr/bin/env python3
"""Validate and append the TECT mainline direction-control ledger.

The direction-control layer is a routing aid.  It prevents repeated finite or
auxiliary work from displacing the active proof obligation while leaving claim,
tier, gate, physical-identity, and empirical transitions protected by the
existing governance.  The machine policy is in
``strategy/mainline-direction-control-v1.json`` and the append-only decision
ledger is in ``strategy/direction-control-log.jsonl``.

Usage:
    python verification/scripts/check_direction_control.py
    python verification/scripts/check_direction_control.py --self-test
    python verification/scripts/check_direction_control.py --add --file record.json
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
__first_issued__ = "2026-08-31"
__version_issued__ = "2026-08-31"

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "mainline-direction-control-v1.json"
LEDGER = REPO / "strategy" / "direction-control-log.jsonl"
LEDGER_REL = "strategy/direction-control-log.jsonl"
SCHEMA = "tect/mainline-direction-control/1.0"
CONTROL_CLASSES = {
    "MAINLINE_ADVANCE",
    "AUXILIARY_SUPPORT",
    "NEGATIVE_RESULT",
    "NO_PROGRESS",
}
LANES = {"forward", "inverse", "auxiliary", "cross-project"}
ROUTES = {
    "BASELINE",
    "CONTINUE_MAINLINE",
    "CONTINUE_PARALLEL",
    "CONTINUE_AUXILIARY",
    "STOP_AUXILIARY_AND_RETURN_TO_MAINLINE",
    "RETURN_TO_MAINLINE",
    "REQUIRE_COUNTEREXAMPLE_OR_REDESIGN",
    "PARK_OR_BLOCK",
}
RECORD_TYPES = {"baseline", "decision"}
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ID_RE = re.compile(r"^DCTRL-(\d{6})$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_RE = re.compile(r"^T-\d{3}$")
HOSTILE_TEST_MINIMUM = 10  # tooling threshold, not a research-derived number

REQUIRED_MANIFEST_KEYS = {
    "active_mainline",
    "authority",
    "auxiliary_scope",
    "baseline",
    "claim_bearing",
    "classification_taxonomy",
    "id",
    "ledger_path",
    "parallel_lanes",
    "policy_path",
    "promotion_order",
    "protected_actions",
    "recorded_on",
    "required_decision_fields",
    "schema",
    "source_program_path",
    "status",
    "tier",
    "thresholds",
    "version",
}
REQUIRED_DECISION_FIELDS = {
    "active_gate",
    "blocker_fingerprint",
    "classification",
    "counts_as_mainline",
    "falsifier_fired",
    "gate_changed",
    "input_hash",
    "lane",
    "mainline_relevant",
    "new_input_hash",
    "next_action",
    "research_admission",
    "route_decision",
    "scope_strengthened",
    "scientific_transition",
    "source_event",
    "task_id",
}
RECORD_METADATA_FIELDS = {
    "id",
    "record_type",
    "recorded_at",
    "recorded_by",
    "schema",
}
OPTIONAL_POINTER_FIELDS = {
    "event_id",
    "evidence_refs",
    "exploration_id",
    "negative_id",
    "notes",
    "result_id",
    "route_reason",
}


def canonical_line(record: dict[str, Any]) -> bytes:
    return (
        json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_repo_path(raw: object) -> Path | None:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute():
        return None
    candidate = (REPO / raw).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return None
    return candidate


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return value is not None


def _registered_tasks() -> set[str]:
    payload = load_json(REPO / "todo" / "todo.json")
    return {
        str(item.get("id"))
        for item in payload.get("tasks", [])
        if isinstance(item, dict) and item.get("id")
    }


def _registered_gate_text() -> str:
    return (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(manifest) != REQUIRED_MANIFEST_KEYS:
        errors.append("manifest fields drifted")
    if manifest.get("schema") != SCHEMA:
        errors.append(f"manifest schema must be {SCHEMA}")
    if manifest.get("id") != "TECT-MAINLINE-DIRECTION-CONTROL-v1":
        errors.append("manifest id drifted")
    if manifest.get("claim_bearing") is not False:
        errors.append("direction-control manifest must remain claim_bearing=false")
    if manifest.get("tier") != "T0":
        errors.append("direction-control manifest must remain T0")
    if manifest.get("status") != "ACTIVE_POLICY_BASELINE":
        errors.append("direction-control manifest status drifted")
    try:
        dt.date.fromisoformat(str(manifest.get("recorded_on")))
    except ValueError:
        errors.append("manifest recorded_on must be an ISO date")

    for field in ("policy_path", "source_program_path", "ledger_path"):
        path = safe_repo_path(manifest.get(field))
        if path is None or not path.is_file():
            errors.append(f"{field} is missing or unsafe")
    source = safe_repo_path(manifest.get("source_program_path"))
    if source is not None and source.is_file():
        try:
            source_data = load_json(source)
            if source_data.get("schema") != "tect/main-proof-program/1.0":
                errors.append("source proof programme schema drifted")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"source proof programme cannot be read: {exc}")

    active = manifest.get("active_mainline")
    if not isinstance(active, dict) or set(active) != {
        "gate_id",
        "lane",
        "last_gate_change_event",
        "next_required_action",
        "required_result",
        "task_id",
    }:
        errors.append("active_mainline fields drifted")
    else:
        if active.get("lane") != "forward":
            errors.append("active mainline must remain the forward lane")
        if active.get("task_id") != "T-054":
            errors.append("active mainline task must remain T-054")
        if not isinstance(active.get("required_result"), list) or not active[
            "required_result"
        ]:
            errors.append("active mainline required_result must be nonempty")
        if not nonempty(active.get("next_required_action")):
            errors.append("active mainline next_required_action is missing")

    tasks = _registered_tasks()
    if active and active.get("task_id") not in tasks:
        errors.append("active mainline task is not registered")
    gates = _registered_gate_text()
    if active and str(active.get("gate_id")) not in gates:
        errors.append("active mainline gate is not registered")

    parallel = manifest.get("parallel_lanes")
    if not isinstance(parallel, list) or len(parallel) != 1:
        errors.append("parallel_lanes must contain exactly one protected inverse lane")
    else:
        item = parallel[0]
        if not isinstance(item, dict) or set(item) != {
            "gate_id",
            "lane",
            "must_not_be_starved",
            "role",
            "task_ids",
        }:
            errors.append("parallel lane fields drifted")
        else:
            if item.get("lane") != "inverse" or item.get("role") != "parallel-critical":
                errors.append("inverse lane role drifted")
            if item.get("must_not_be_starved") is not True:
                errors.append("inverse lane starvation guard is missing")
            if item.get("task_ids") != ["T-059", "T-061"]:
                errors.append("inverse lane task order drifted")
            if item.get("gate_id") not in gates:
                errors.append("inverse lane gate is not registered")
            for task_id in item.get("task_ids", []):
                if task_id not in tasks:
                    errors.append(f"inverse lane task is not registered: {task_id}")

    auxiliary = manifest.get("auxiliary_scope")
    if not isinstance(auxiliary, list) or not auxiliary:
        errors.append("auxiliary_scope must be nonempty")
    else:
        for item in auxiliary:
            if not isinstance(item, dict) or set(item) != {"name", "role", "task_ids"}:
                errors.append("auxiliary scope fields drifted")
                continue
            if not nonempty(item.get("name")) or not nonempty(item.get("role")):
                errors.append("auxiliary scope name/role missing")
            if not isinstance(item.get("task_ids"), list):
                errors.append("auxiliary scope task_ids must be a list")
            for task_id in item.get("task_ids", []):
                if task_id not in tasks:
                    errors.append(f"auxiliary task is not registered: {task_id}")

    taxonomy = manifest.get("classification_taxonomy")
    if not isinstance(taxonomy, dict) or set(taxonomy) != CONTROL_CLASSES:
        errors.append("classification taxonomy drifted")
    else:
        for name, item in taxonomy.items():
            if not isinstance(item, dict) or set(item) != {
                "counts_as_mainline",
                "description",
                "required_signal",
            }:
                errors.append(f"taxonomy fields drifted for {name}")
                continue
            counts = item.get("counts_as_mainline")
            if name == "NEGATIVE_RESULT":
                if counts != "record_decides":
                    errors.append("negative-result taxonomy must be record_decides")
            elif counts != (name == "MAINLINE_ADVANCE"):
                errors.append(f"taxonomy count flag drifted for {name}")
            if not nonempty(item.get("description")) or not nonempty(
                item.get("required_signal")
            ):
                errors.append(f"taxonomy prose missing for {name}")

    thresholds = manifest.get("thresholds")
    threshold_keys = {
        "max_auxiliary_streak",
        "max_checkpoints_without_gate_change",
        "same_blocker_park_at",
        "same_blocker_redesign_at",
    }
    if not isinstance(thresholds, dict) or set(thresholds) != threshold_keys:
        errors.append("direction thresholds drifted")
    else:
        for key, value in thresholds.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                errors.append(f"threshold {key} must be a positive integer")
        if isinstance(thresholds.get("same_blocker_redesign_at"), int) and isinstance(
            thresholds.get("same_blocker_park_at"), int
        ) and thresholds["same_blocker_redesign_at"] >= thresholds[
            "same_blocker_park_at"
        ]:
            errors.append("redesign threshold must precede park threshold")

    if manifest.get("promotion_order") != [
        "source-compatible",
        "uniform",
        "physical-sector",
        "limit",
    ]:
        errors.append("promotion order drifted")
    protected = " ".join(str(item) for item in manifest.get("protected_actions", []))
    protected_low = protected.lower()
    for token in ("operator-authorized", "never auto-approved", "research admission"):
        if token not in protected_low:
            errors.append(f"protected action text lacks {token!r}")

    baseline = manifest.get("baseline")
    baseline_keys = {
        "auxiliary_streak",
        "checkpoints_without_gate_change",
        "cutover_date",
        "cutover_event",
        "historical_records_before_cutover",
        "no_progress_streak",
        "same_blocker_streak",
        "note",
    }
    if not isinstance(baseline, dict) or set(baseline) != baseline_keys:
        errors.append("baseline fields drifted")
    else:
        for key in (
            "auxiliary_streak",
            "checkpoints_without_gate_change",
            "no_progress_streak",
            "same_blocker_streak",
        ):
            value = baseline.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"baseline counter {key} must be nonnegative")
        try:
            dt.date.fromisoformat(str(baseline.get("cutover_date")))
        except ValueError:
            errors.append("baseline cutover_date must be an ISO date")
        if not nonempty(baseline.get("cutover_event")) or not nonempty(
            baseline.get("historical_records_before_cutover")
        ):
            errors.append("baseline cutover metadata is incomplete")

    required_fields = manifest.get("required_decision_fields")
    if not isinstance(required_fields, list) or set(required_fields) != REQUIRED_DECISION_FIELDS:
        errors.append("required decision fields drifted")

    return errors


def _record_error(index: int, message: str) -> str:
    return f"record {index}: {message}"


def _validate_record_shape(
    record: dict[str, Any], index: int, manifest: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    identifier = str(record.get("id", ""))
    match = ID_RE.fullmatch(identifier)
    if not match:
        errors.append(_record_error(index, f"invalid id {identifier!r}"))
    if record.get("schema") != SCHEMA:
        errors.append(_record_error(index, "schema drifted"))
    record_type = record.get("record_type")
    if record_type not in RECORD_TYPES:
        errors.append(_record_error(index, f"invalid record_type {record_type!r}"))
    recorded_at = str(record.get("recorded_at", ""))
    if not UTC_RE.fullmatch(recorded_at):
        errors.append(_record_error(index, "recorded_at must be second-precision UTC"))
    else:
        try:
            dt.datetime.strptime(recorded_at, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            errors.append(_record_error(index, "recorded_at is not a valid UTC time"))
    if not nonempty(record.get("recorded_by")):
        errors.append(_record_error(index, "recorded_by is missing"))

    required = REQUIRED_DECISION_FIELDS if record_type == "decision" else {
        "active_gate",
        "blocker_fingerprint",
        "classification",
        "counts_as_mainline",
        "falsifier_fired",
        "gate_changed",
        "input_hash",
        "lane",
        "mainline_relevant",
        "new_input_hash",
        "next_action",
        "research_admission",
        "route_decision",
        "scope_strengthened",
        "scientific_transition",
        "source_event",
        "task_id",
    }
    missing = sorted(field for field in required if field not in record)
    for field in missing:
        errors.append(_record_error(index, f"missing field {field}"))
    if missing:
        return errors

    classification = record.get("classification")
    if record_type == "baseline":
        if classification != "BASELINE":
            errors.append(_record_error(index, "baseline classification must be BASELINE"))
        if record.get("route_decision") != "BASELINE":
            errors.append(_record_error(index, "baseline route must be BASELINE"))
    elif classification not in CONTROL_CLASSES:
        errors.append(_record_error(index, f"invalid classification {classification!r}"))

    if record.get("lane") not in LANES:
        errors.append(_record_error(index, "invalid lane"))
    if not TASK_RE.fullmatch(str(record.get("task_id", ""))):
        errors.append(_record_error(index, "task_id must match T-NNN"))
    if not nonempty(record.get("active_gate")):
        errors.append(_record_error(index, "active_gate is missing"))
    if not nonempty(record.get("source_event")):
        errors.append(_record_error(index, "source_event is missing"))
    if not nonempty(record.get("blocker_fingerprint")):
        errors.append(_record_error(index, "blocker_fingerprint is missing"))
    if record.get("input_hash") != "NONE" and not HASH_RE.fullmatch(
        str(record.get("input_hash", ""))
    ):
        errors.append(_record_error(index, "input_hash must be NONE or a SHA-256"))
    if record.get("new_input_hash") is True and record.get("input_hash") == "NONE":
        errors.append(_record_error(index, "new_input_hash requires a SHA-256 input_hash"))
    for field in (
        "counts_as_mainline",
        "falsifier_fired",
        "gate_changed",
        "mainline_relevant",
        "new_input_hash",
        "research_admission",
        "scope_strengthened",
        "scientific_transition",
    ):
        if not isinstance(record.get(field), bool):
            errors.append(_record_error(index, f"{field} must be boolean"))
    if not nonempty(record.get("next_action")):
        errors.append(_record_error(index, "next_action is missing"))
    if record.get("route_decision") not in ROUTES:
        errors.append(_record_error(index, "invalid route_decision"))
    if record.get("research_admission") is not True:
        errors.append(_record_error(index, "research_admission must be true"))
    if record.get("scientific_transition") is not False:
        errors.append(_record_error(index, "scientific_transition must remain false"))

    if record_type == "baseline":
        for field in (
            "counts_as_mainline",
            "falsifier_fired",
            "gate_changed",
            "mainline_relevant",
            "new_input_hash",
            "scope_strengthened",
        ):
            if record.get(field) is not False:
                errors.append(_record_error(index, f"baseline {field} must be false"))
        if record.get("input_hash") != "NONE":
            errors.append(_record_error(index, "baseline input_hash must be NONE"))
        return errors

    classification = str(record.get("classification"))
    counts = record.get("counts_as_mainline")
    relevant = record.get("mainline_relevant")
    if classification == "MAINLINE_ADVANCE":
        if counts is not True or relevant is not True:
            errors.append(_record_error(index, "MAINLINE_ADVANCE must count as mainline"))
        if not any(
            record.get(field) is True
            for field in ("gate_changed", "scope_strengthened", "new_input_hash")
        ):
            errors.append(_record_error(index, "MAINLINE_ADVANCE lacks a scope signal"))
    elif classification == "AUXILIARY_SUPPORT":
        if counts is not False or relevant is not False:
            errors.append(_record_error(index, "AUXILIARY_SUPPORT cannot count as mainline"))
        if record.get("gate_changed") or record.get("scope_strengthened"):
            errors.append(_record_error(index, "AUXILIARY_SUPPORT has a mainline signal"))
        if record.get("falsifier_fired"):
            errors.append(_record_error(index, "AUXILIARY_SUPPORT must not hide a falsifier"))
    elif classification == "NO_PROGRESS":
        if counts is not False or relevant is not False:
            errors.append(_record_error(index, "NO_PROGRESS cannot count as mainline"))
        if record.get("gate_changed") or record.get("scope_strengthened"):
            errors.append(_record_error(index, "NO_PROGRESS has a gate or scope change"))
        if record.get("falsifier_fired"):
            errors.append(_record_error(index, "NO_PROGRESS must not hide a falsifier"))
    elif classification == "NEGATIVE_RESULT":
        if record.get("falsifier_fired") is not True:
            errors.append(_record_error(index, "NEGATIVE_RESULT must fire a falsifier"))
        if counts != relevant:
            errors.append(_record_error(index, "negative mainline relevance/count mismatch"))
    return errors


def parse_ledger(path: Path) -> tuple[list[dict[str, Any]], list[str], bytes]:
    errors: list[str] = []
    if not path.is_file():
        return [], [f"missing ledger: {path.relative_to(REPO)}"], b""
    raw = path.read_bytes()
    if b"\r" in raw.replace(b"\r\n", b""):
        errors.append("ledger contains a bare CR byte")
    if raw and not raw.replace(b"\r\n", b"\n").endswith(b"\n"):
        errors.append("ledger must end with LF")
    records: list[dict[str, Any]] = []
    normalized = raw.replace(b"\r\n", b"\n")
    for number, line in enumerate(normalized.splitlines(keepends=True), start=1):
        if not line.strip():
            errors.append(f"line {number}: blank lines are forbidden")
            continue
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"line {number}: invalid UTF-8/JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {number}: record must be an object")
            continue
        if line != canonical_line(record):
            errors.append(f"line {number}: non-canonical JSON encoding")
        records.append(record)
    return records, errors, raw


def derive_state(
    manifest: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any]:
    baseline = manifest["baseline"]
    state = {
        "auxiliary_streak": baseline["auxiliary_streak"],
        "no_progress_streak": baseline["no_progress_streak"],
        "checkpoints_without_gate_change": baseline["checkpoints_without_gate_change"],
        "same_blocker_streak": baseline["same_blocker_streak"],
        "last_blocker": None,
        "last_classification": "BASELINE",
        "last_route": "BASELINE",
    }
    for record in records[1:]:
        classification = record["classification"]
        if classification in {"AUXILIARY_SUPPORT", "NO_PROGRESS"}:
            state["auxiliary_streak"] += 1
        else:
            state["auxiliary_streak"] = 0
        if classification == "NO_PROGRESS":
            state["no_progress_streak"] += 1
        else:
            state["no_progress_streak"] = 0
        if record["gate_changed"]:
            state["checkpoints_without_gate_change"] = 0
        else:
            state["checkpoints_without_gate_change"] += 1
        blocker = record["blocker_fingerprint"]
        if blocker in {"", "NONE"}:
            state["same_blocker_streak"] = 0
            state["last_blocker"] = None
        elif blocker == state["last_blocker"]:
            state["same_blocker_streak"] += 1
        else:
            state["same_blocker_streak"] = 1
            state["last_blocker"] = blocker
        state["last_classification"] = classification
        state["last_route"] = record["route_decision"]
    return state


def route_for_state(
    manifest: dict[str, Any], state: dict[str, Any], record: dict[str, Any]
) -> str:
    if record.get("record_type") == "baseline":
        return "BASELINE"
    thresholds = manifest["thresholds"]
    if state["same_blocker_streak"] >= thresholds["same_blocker_park_at"]:
        return "PARK_OR_BLOCK"
    if state["same_blocker_streak"] >= thresholds["same_blocker_redesign_at"]:
        return "REQUIRE_COUNTEREXAMPLE_OR_REDESIGN"
    if state["auxiliary_streak"] >= thresholds["max_auxiliary_streak"]:
        return "STOP_AUXILIARY_AND_RETURN_TO_MAINLINE"
    if (
        state["checkpoints_without_gate_change"]
        >= thresholds["max_checkpoints_without_gate_change"]
    ):
        return "RETURN_TO_MAINLINE"
    if record["mainline_relevant"]:
        return "CONTINUE_MAINLINE"
    if record["lane"] == "inverse":
        return "CONTINUE_PARALLEL"
    return "CONTINUE_AUXILIARY"


def _committed_prefix_error(current: bytes) -> str | None:
    git = shutil.which("git")
    if not git:
        return None
    result = subprocess.run(
        [git, "show", f"HEAD:{LEDGER_REL}"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    committed = result.stdout.replace(b"\r\n", b"\n")
    if not current.replace(b"\r\n", b"\n").startswith(committed):
        return "ledger does not preserve the committed ledger as an immutable prefix"
    return None


def validate_ledger(
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
    raw: bytes,
    check_git: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not records:
        return ["ledger must contain a baseline record"]
    seen: set[str] = set()
    previous_time = ""
    for index, record in enumerate(records, start=1):
        errors.extend(_validate_record_shape(record, index, manifest))
        identifier = str(record.get("id", ""))
        match = ID_RE.fullmatch(identifier)
        if match:
            expected = f"DCTRL-{index:06d}"
            if identifier != expected:
                errors.append(_record_error(index, f"expected {expected}, got {identifier}"))
        if identifier in seen:
            errors.append(_record_error(index, "duplicate id"))
        seen.add(identifier)
        recorded_at = str(record.get("recorded_at", ""))
        if UTC_RE.fullmatch(recorded_at) and recorded_at < previous_time:
            errors.append(_record_error(index, "recorded_at is not append-order monotone"))
        if UTC_RE.fullmatch(recorded_at):
            previous_time = recorded_at
        if index == 1:
            if record.get("record_type") != "baseline":
                errors.append("first record must be a baseline")
            if record.get("source_event") != manifest["baseline"]["cutover_event"]:
                errors.append("baseline source_event does not match the cutover event")
        elif record.get("record_type") != "decision":
            errors.append(_record_error(index, "only the first record may be baseline"))

    if records[0].get("record_type") == "baseline":
        state = derive_state(manifest, records[:1])
        if state["last_route"] != "BASELINE":
            errors.append("baseline state is malformed")
    for index, record in enumerate(records[1:], start=2):
        if record.get("record_type") != "decision":
            continue
        state = derive_state(manifest, records[:index])
        expected_route = route_for_state(manifest, state, record)
        if record.get("route_decision") != expected_route:
            errors.append(
                _record_error(
                    index,
                    f"route_decision {record.get('route_decision')!r} != {expected_route!r}",
                )
            )
    if check_git:
        prefix_error = _committed_prefix_error(raw)
        if prefix_error:
            errors.append(prefix_error)
    return errors


def load_live() -> tuple[dict[str, Any], list[dict[str, Any]], bytes, list[str]]:
    try:
        manifest = load_json(MANIFEST)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [], b"", [f"cannot load manifest: {exc}"]
    if not isinstance(manifest, dict):
        return {}, [], b"", ["manifest root must be an object"]
    manifest_errors = validate_manifest(manifest)
    records, ledger_errors, raw = parse_ledger(LEDGER)
    errors = manifest_errors + ledger_errors
    if not manifest_errors and not ledger_errors:
        errors.extend(validate_ledger(manifest, records, raw))
    return manifest, records, raw, errors


def _now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_check() -> int:
    manifest, records, raw, errors = load_live()
    if errors:
        print("DIRECTION-CONTROL: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    state = derive_state(manifest, records)
    last = records[-1]
    action = route_for_state(manifest, state, last)
    print(
        "DIRECTION-CONTROL: PASS "
        f"(mainline={manifest['active_mainline']['task_id']}; "
        f"gate={manifest['active_mainline']['gate_id']}; "
        f"auxiliary_streak={state['auxiliary_streak']}; "
        f"no_progress_streak={state['no_progress_streak']}; "
        f"same_blocker_streak={state['same_blocker_streak']}; "
        f"route={action}; records={len(records)})"
    )
    return 0


def cmd_add(path_text: str) -> int:
    manifest, records, raw, errors = load_live()
    if errors:
        print("DIRECTION-CONTROL: ADD REFUSED; current ledger failed integrity")
        for error in errors:
            print(f"  - {error}")
        return 1
    try:
        payload = json.loads(
            sys.stdin.read() if path_text == "-" else Path(path_text).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"DIRECTION-CONTROL: ADD REFUSED; {exc}")
        return 1
    if not isinstance(payload, dict):
        print("DIRECTION-CONTROL: ADD REFUSED; input must be one decision object")
        return 1
    record = dict(payload)
    next_id = f"DCTRL-{len(records) + 1:06d}"
    if "id" in record and record["id"] != next_id:
        print(f"DIRECTION-CONTROL: ADD REFUSED; next immutable id is {next_id}")
        return 1
    record["id"] = next_id
    record.setdefault("schema", SCHEMA)
    record.setdefault("record_type", "decision")
    record.setdefault("recorded_at", _now_utc())
    record.setdefault("recorded_by", "Codex")
    record.setdefault("research_admission", True)
    record.setdefault("scientific_transition", False)
    record.setdefault("input_hash", "NONE")
    record.setdefault("blocker_fingerprint", "NONE")
    record.setdefault("gate_changed", False)
    record.setdefault("scope_strengthened", False)
    record.setdefault("new_input_hash", False)
    record.setdefault("falsifier_fired", False)
    record.setdefault("mainline_relevant", record.get("classification") == "MAINLINE_ADVANCE")
    record.setdefault("counts_as_mainline", record.get("mainline_relevant", False))
    record.setdefault("route_decision", "CONTINUE_AUXILIARY")
    candidate_records = records + [record]
    state = derive_state(manifest, candidate_records)
    record["route_decision"] = route_for_state(manifest, state, record)
    candidate_records = records + [record]
    candidate_errors = validate_ledger(manifest, candidate_records, raw, check_git=False)
    if candidate_errors:
        print("DIRECTION-CONTROL: ADD REFUSED; proposed record failed validation")
        for error in candidate_errors:
            print(f"  - {error}")
        return 1
    atomic_write(LEDGER, raw + canonical_line(record))
    print(
        f"DIRECTION-CONTROL: appended {record['id']} "
        f"({record['classification']}; route={record['route_decision']})"
    )
    return 0


def _valid_decision(
    base: dict[str, Any],
    identifier: str,
    recorded_at: str,
    classification: str,
    lane: str = "auxiliary",
    blocker: str = "NEW-BLOCKER",
) -> dict[str, Any]:
    record = copy.deepcopy(base)
    record.update(
        {
            "id": identifier,
            "record_type": "decision",
            "recorded_at": recorded_at,
            "classification": classification,
            "lane": lane,
            "blocker_fingerprint": blocker,
            "source_event": "EXP-TEST",
            "task_id": "T-055",
            "active_gate": "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
            "next_action": "Run the declared next action.",
            "input_hash": "NONE",
            "gate_changed": False,
            "scope_strengthened": False,
            "new_input_hash": False,
            "falsifier_fired": classification == "NEGATIVE_RESULT",
            "mainline_relevant": classification == "MAINLINE_ADVANCE",
            "counts_as_mainline": classification == "MAINLINE_ADVANCE",
            "research_admission": True,
            "scientific_transition": False,
            "route_decision": "CONTINUE_AUXILIARY",
        }
    )
    return record


def self_test() -> int:
    manifest = load_json(MANIFEST)
    records, parse_errors, raw = parse_ledger(LEDGER)
    assert not validate_manifest(manifest)
    assert not parse_errors
    assert not validate_ledger(manifest, records, raw, check_git=False)
    baseline = records[0]
    base = {
        "schema": SCHEMA,
        "recorded_by": "self-test",
        "research_admission": True,
        "scientific_transition": False,
    }

    valid = _valid_decision(
        base,
        "DCTRL-000002",
        "2026-08-31T00:00:01Z",
        "AUXILIARY_SUPPORT",
        blocker="TEST-BLOCKER-A",
    )
    test_records = [baseline, valid]
    state = derive_state(manifest, test_records)
    valid["route_decision"] = route_for_state(manifest, state, valid)
    assert not validate_ledger(manifest, test_records, raw, check_git=False)

    # Exercise each automatic boundary with synthetic, non-persistent records.
    second = _valid_decision(
        base,
        "DCTRL-000003",
        "2026-08-31T00:00:02Z",
        "AUXILIARY_SUPPORT",
        blocker="TEST-BLOCKER-B",
    )
    two_records = [baseline, valid, second]
    second["route_decision"] = route_for_state(
        manifest, derive_state(manifest, two_records), second
    )
    assert second["route_decision"] == "STOP_AUXILIARY_AND_RETURN_TO_MAINLINE"
    assert not validate_ledger(manifest, two_records, raw, check_git=False)

    same_one = _valid_decision(
        base,
        "DCTRL-000002",
        "2026-08-31T00:00:02Z",
        "AUXILIARY_SUPPORT",
        blocker="TEST-SAME",
    )
    same_two = _valid_decision(
        base,
        "DCTRL-000003",
        "2026-08-31T00:00:03Z",
        "AUXILIARY_SUPPORT",
        blocker="TEST-SAME",
    )
    same_records = [baseline, same_one, same_two]
    same_one["route_decision"] = route_for_state(
        manifest, derive_state(manifest, same_records[:2]), same_one
    )
    same_two["route_decision"] = route_for_state(
        manifest, derive_state(manifest, same_records), same_two
    )
    assert same_two["route_decision"] == "REQUIRE_COUNTEREXAMPLE_OR_REDESIGN"
    assert not validate_ledger(manifest, same_records, raw, check_git=False)

    hostile_mutations: list[tuple[str, Any]] = []

    def add_hostile(name: str, mutate) -> None:
        hostile_mutations.append((name, mutate))

    add_hostile("wrong schema", lambda item: item.__setitem__("schema", "bad/schema"))
    add_hostile("wrong type", lambda item: item.__setitem__("record_type", "baseline"))
    add_hostile("wrong class", lambda item: item.__setitem__("classification", "UNKNOWN"))
    add_hostile("missing next action", lambda item: item.pop("next_action"))
    add_hostile("research admission off", lambda item: item.__setitem__("research_admission", False))
    add_hostile("scientific transition", lambda item: item.__setitem__("scientific_transition", True))
    add_hostile("counts mismatch", lambda item: item.__setitem__("counts_as_mainline", True))
    add_hostile("mainline without signal", lambda item: (item.__setitem__("classification", "MAINLINE_ADVANCE"), item.__setitem__("mainline_relevant", True), item.__setitem__("counts_as_mainline", True)))
    add_hostile("bad hash", lambda item: item.__setitem__("input_hash", "1234"))
    add_hostile("route mismatch", lambda item: item.__setitem__("route_decision", "CONTINUE_MAINLINE"))
    add_hostile("duplicate id", lambda item: item.__setitem__("id", "DCTRL-000001"))
    add_hostile("time reversal", lambda item: item.__setitem__("recorded_at", "2020-01-01T00:00:00Z"))

    rejected = 0
    for name, mutate in hostile_mutations:
        candidate = copy.deepcopy(valid)
        mutate(candidate)
        candidate_records = [baseline, candidate]
        errors = validate_ledger(manifest, candidate_records, raw, check_git=False)
        assert errors, f"hostile mutation accepted: {name}"
        rejected += 1
    assert rejected >= HOSTILE_TEST_MINIMUM
    print(
        "DIRECTION-CONTROL SELFTEST: PASS "
        f"({rejected} hostile mutations rejected; threshold={HOSTILE_TEST_MINIMUM})"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--add", action="store_true", help="append one decision record")
    parser.add_argument("--file", default=None, help="JSON record path, or - for stdin")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.add:
        if not args.file:
            print("DIRECTION-CONTROL: --add requires --file <path|->")
            return 2
        return cmd_add(args.file)
    return cmd_check()


if __name__ == "__main__":
    raise SystemExit(main())
