#!/usr/bin/env python3
"""Fail-closed wall-clock provenance audit for the exploration ledger.

The exploration ID ordinal is immutable authority.  A separate append-only
sidecar may mark a historically recorded ``recorded_at`` value as untrusted;
it never rewrites the exploration, its scientific content, or its verdict.
"""

__version__ = "1.0.0"
__first_issued__ = "2026-08-30"
__version_issued__ = "2026-08-30"

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "explorations" / "log.jsonl"
CORRECTIONS = REPO / "explorations" / "temporal-corrections.jsonl"
SCHEMA = "tect/exploration-time-correction/1.0"
EXP_RE = re.compile(r"EXP-(\d{6})\Z")
TC_RE = re.compile(r"TC-(\d{4})\Z")
UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
SKEW_SECONDS = 300


def canonical_line(record: dict) -> bytes:
    return (
        json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def normalize_eol(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n")


def parse_utc(value: object, label: str, errors: list[str]) -> dt.datetime | None:
    text = str(value)
    if not UTC_RE.fullmatch(text):
        errors.append(f"{label}: must be second-precision UTC")
        return None
    try:
        return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc
        )
    except ValueError:
        errors.append(f"{label}: invalid timestamp {text!r}")
        return None


def parse_jsonl(path: Path) -> tuple[list[dict], bytes, list[str]]:
    raw = path.read_bytes() if path.exists() else b""
    normalized = normalize_eol(raw)
    errors: list[str] = []
    if b"\r" in raw.replace(b"\r\n", b""):
        errors.append(f"{path.name}: bare CR byte")
    if normalized and not normalized.endswith(b"\n"):
        errors.append(f"{path.name}: final LF missing")
    records: list[dict] = []
    for line_number, line in enumerate(normalized.splitlines(keepends=True), start=1):
        if not line.strip():
            errors.append(f"{path.name}:{line_number}: blank line")
            continue
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}:{line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.name}:{line_number}: object required")
            continue
        if line != canonical_line(record):
            errors.append(f"{path.name}:{line_number}: non-canonical JSON")
        records.append(record)
    return records, raw, errors


def _expand_range(first_id: str, last_id: str) -> list[str]:
    first_match = EXP_RE.fullmatch(first_id)
    last_match = EXP_RE.fullmatch(last_id)
    if not first_match or not last_match:
        raise ValueError("range endpoints must be EXP-NNNNNN")
    first = int(first_match.group(1))
    last = int(last_match.group(1))
    if first > last:
        raise ValueError("range first_id exceeds last_id")
    return [f"EXP-{number:06d}" for number in range(first, last + 1)]


def validate_correction_records(
    correction_records: list[dict], exploration_records: list[dict]
) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    known_ids = {str(record.get("id", "")) for record in exploration_records}
    corrected: set[str] = set()
    required = {
        "schema",
        "id",
        "registered_at",
        "registered_by",
        "audit_basis",
        "corrections",
        "authority",
        "boundary",
        "non_claims",
    }
    for index, record in enumerate(correction_records, start=1):
        prefix = f"correction {index}"
        if set(record) != required:
            errors.append(f"{prefix}: fields must be exactly {sorted(required)}")
        if record.get("schema") != SCHEMA:
            errors.append(f"{prefix}: schema must be {SCHEMA}")
        identifier = str(record.get("id", ""))
        match = TC_RE.fullmatch(identifier)
        if not match or int(match.group(1)) != index:
            errors.append(f"{prefix}: expected TC-{index:04d}, got {identifier!r}")
        parse_utc(record.get("registered_at"), f"{prefix}.registered_at", errors)
        if not isinstance(record.get("registered_by"), str) or not record.get(
            "registered_by", ""
        ).strip():
            errors.append(f"{prefix}: registered_by must be nonempty")
        for field in ("authority", "boundary"):
            if not isinstance(record.get(field), str) or not record.get(field, "").strip():
                errors.append(f"{prefix}: {field} must be nonempty")
        non_claims = record.get("non_claims")
        if not isinstance(non_claims, list) or not non_claims or any(
            not isinstance(item, str) or not item.strip() for item in non_claims
        ):
            errors.append(f"{prefix}: non_claims must be nonempty strings")

        basis = record.get("audit_basis")
        basis_required = {
            "audit_utc",
            "head",
            "method",
            "allowed_future_skew_seconds",
            "record_count",
            "head_record_count",
            "offender_count",
        }
        if not isinstance(basis, dict) or set(basis) != basis_required:
            errors.append(f"{prefix}: malformed audit_basis")
            basis = {}
        parse_utc(basis.get("audit_utc"), f"{prefix}.audit_basis.audit_utc", errors)
        if basis.get("allowed_future_skew_seconds") != SKEW_SECONDS:
            errors.append(f"{prefix}: skew must be {SKEW_SECONDS} seconds")
        if not re.fullmatch(r"[0-9a-f]{40}", str(basis.get("head", ""))):
            errors.append(f"{prefix}: audit head must be a full lowercase SHA-1")
        if not isinstance(basis.get("method"), str) or not basis.get("method", "").strip():
            errors.append(f"{prefix}: audit method must be nonempty")
        for field in ("record_count", "head_record_count", "offender_count"):
            if not isinstance(basis.get(field), int) or basis.get(field, -1) < 0:
                errors.append(f"{prefix}: audit_basis.{field} must be nonnegative int")

        ranges = record.get("corrections")
        if not isinstance(ranges, list) or not ranges:
            errors.append(f"{prefix}: corrections must be nonempty")
            ranges = []
        local_count = 0
        for range_index, item in enumerate(ranges, start=1):
            range_prefix = f"{prefix}.corrections[{range_index}]"
            if not isinstance(item, dict) or set(item) != {
                "first_id",
                "last_id",
                "field",
                "replacement",
            }:
                errors.append(f"{range_prefix}: malformed range")
                continue
            if item.get("field") != "recorded_at" or item.get("replacement") != "UNKNOWN":
                errors.append(f"{range_prefix}: only recorded_at -> UNKNOWN is allowed")
            try:
                identifiers = _expand_range(
                    str(item.get("first_id", "")), str(item.get("last_id", ""))
                )
            except ValueError as exc:
                errors.append(f"{range_prefix}: {exc}")
                continue
            local_count += len(identifiers)
            for exploration_id in identifiers:
                if exploration_id in corrected:
                    errors.append(f"{range_prefix}: overlapping id {exploration_id}")
                corrected.add(exploration_id)
                if exploration_id not in known_ids:
                    errors.append(f"{range_prefix}: unknown id {exploration_id}")
        if isinstance(basis.get("offender_count"), int) and local_count != basis.get(
            "offender_count"
        ):
            errors.append(
                f"{prefix}: range count {local_count} != offender_count "
                f"{basis.get('offender_count')}"
            )
    return corrected, errors


def _find_git() -> str | None:
    configured = os.environ.get("TECT_GIT")
    if configured and Path(configured).is_file():
        return configured
    return shutil.which("git")


def _head_bytes(git: str, repo_path: str) -> tuple[bytes | None, str | None]:
    exists = subprocess.run(
        [git, "cat-file", "-e", f"HEAD:{repo_path}"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if exists.returncode != 0:
        return None, None
    shown = subprocess.run(
        [git, "show", f"HEAD:{repo_path}"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if shown.returncode != 0:
        return None, shown.stderr.decode("utf-8", errors="replace").strip()
    return shown.stdout, None


def _append_only_error(current: bytes, committed: bytes | None) -> str | None:
    if committed is None:
        return None
    if not normalize_eol(current).startswith(normalize_eol(committed)):
        return "temporal correction sidecar does not preserve git HEAD as a prefix"
    return None


def load_correction_state(
    exploration_records: list[dict], check_git: bool = False
) -> tuple[set[str], list[str]]:
    corrections, raw, errors = parse_jsonl(CORRECTIONS)
    corrected, validation_errors = validate_correction_records(
        corrections, exploration_records
    )
    errors.extend(validation_errors)
    if check_git:
        git = _find_git()
        if not git:
            errors.append("git executable unavailable for correction append-only check")
        else:
            committed, git_error = _head_bytes(
                git, "explorations/temporal-corrections.jsonl"
            )
            if git_error:
                errors.append(f"correction git check failed: {git_error}")
            prefix_error = _append_only_error(raw, committed)
            if prefix_error:
                errors.append(prefix_error)
    return corrected, errors


def _blame_committer_times(git: str) -> tuple[list[int], int, list[str]]:
    errors: list[str] = []
    committed, git_error = _head_bytes(git, "explorations/log.jsonl")
    if git_error:
        return [], 0, [f"log git check failed: {git_error}"]
    if committed is None:
        return [], 0, []
    head_count = len(normalize_eol(committed).splitlines())
    blamed = subprocess.run(
        [git, "blame", "--line-porcelain", "HEAD", "--", "explorations/log.jsonl"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if blamed.returncode != 0:
        return [], head_count, [f"git blame failed: {blamed.stderr.strip()}"]
    times: list[int] = []
    current: int | None = None
    for line in blamed.stdout.splitlines():
        if line.startswith("committer-time "):
            try:
                current = int(line.split()[1])
            except (IndexError, ValueError):
                current = None
        elif line.startswith("\t"):
            if current is None:
                errors.append("git blame emitted a content line without committer-time")
            else:
                times.append(current)
    if len(times) != head_count:
        errors.append(f"git blame line count {len(times)} != HEAD count {head_count}")
    return times, head_count, errors


def audit_wall_clock(
    exploration_records: list[dict], corrected: set[str]
) -> tuple[int, list[str]]:
    errors: list[str] = []
    git = _find_git()
    if not git:
        return 0, ["git executable unavailable for wall-clock provenance audit"]
    times, head_count, blame_errors = _blame_committer_times(git)
    errors.extend(blame_errors)
    now = dt.datetime.now(dt.timezone.utc)
    uncorrected_offenders = 0
    for index, record in enumerate(exploration_records):
        identifier = str(record.get("id", ""))
        stamp = parse_utc(record.get("recorded_at"), f"{identifier}.recorded_at", errors)
        if stamp is None or identifier in corrected:
            continue
        owner_time = (
            dt.datetime.fromtimestamp(times[index], tz=dt.timezone.utc)
            if index < min(head_count, len(times))
            else now
        )
        if stamp > owner_time + dt.timedelta(seconds=SKEW_SECONDS):
            uncorrected_offenders += 1
            errors.append(
                f"{identifier}: recorded_at {stamp.strftime('%Y-%m-%dT%H:%M:%SZ')} "
                f"exceeds first-containing authority time plus {SKEW_SECONDS}s"
            )
    return uncorrected_offenders, errors


def verify() -> tuple[int, int, list[str]]:
    explorations, _, errors = parse_jsonl(LOG)
    corrected, correction_errors = load_correction_state(explorations, check_git=True)
    errors.extend(correction_errors)
    offenders, audit_errors = audit_wall_clock(explorations, corrected)
    errors.extend(audit_errors)
    return len(explorations), len(corrected), errors


def self_test() -> int:
    explorations = [{"id": f"EXP-{number:06d}"} for number in range(1, 6)]
    fixture = {
        "schema": SCHEMA,
        "id": "TC-0001",
        "registered_at": "2026-08-30T00:00:00Z",
        "registered_by": "self-test",
        "audit_basis": {
            "audit_utc": "2026-08-30T00:00:00Z",
            "head": "0" * 40,
            "method": "self-test",
            "allowed_future_skew_seconds": SKEW_SECONDS,
            "record_count": 5,
            "head_record_count": 5,
            "offender_count": 3,
        },
        "corrections": [
            {
                "first_id": "EXP-000002",
                "last_id": "EXP-000004",
                "field": "recorded_at",
                "replacement": "UNKNOWN",
            }
        ],
        "authority": "Ordinal authority only.",
        "boundary": "Wall-clock correction only.",
        "non_claims": ["No scientific verdict changes."],
    }
    corrected, errors = validate_correction_records([fixture], explorations)
    assert corrected == {"EXP-000002", "EXP-000003", "EXP-000004"}
    assert not errors, errors
    broken = json.loads(json.dumps(fixture))
    broken["corrections"][0]["last_id"] = "EXP-000005"
    _, broken_errors = validate_correction_records([broken], explorations)
    assert broken_errors, "range/count mismatch accepted"
    print("EXPLORATION-TIME-SELFTEST: PASS (range, count, schema, canonical UTC)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    record_count, corrected_count, errors = verify()
    if errors:
        print("EXPLORATION-TIME: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        "EXPLORATION-TIME: PASS "
        f"(records={record_count}; corrected-untrusted={corrected_count}; "
        "uncorrected-future=0)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
