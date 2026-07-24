#!/usr/bin/env python3
"""Append-only proof-exploration ledger for TECT.

The ledger records researcher-reusable route decisions without exposing or
pretending to preserve private token-by-token reasoning.  It is not a proof,
tier, gate, result, or negative-result authority.

Canonical source: explorations/log.jsonl (oldest first, immutable lines)
Generated projection: theory/proof-evidence-map.md and
                      verification/proof-evidence-map.json

Usage:
    python verification/scripts/exploration.py add --file record.json
    python verification/scripts/exploration.py add --file -
    python verification/scripts/exploration.py search [filters]
    python verification/scripts/exploration.py verify
    python verification/scripts/exploration.py --self-test
"""

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "explorations" / "log.jsonl"
SCHEMA = "tect/proof-exploration/1.0"
VERDICTS = ("advanced", "failed", "inconclusive", "parked")
PROVENANCE = ("contemporaneous", "historical-backfill")
RELATIONS = ("continues", "alternative_to", "corrects", "supersedes")
CORE_TEXT = (
    "title",
    "question",
    "finding",
    "decision_reason",
    "boundary",
    "next_action",
)
FORMAL_KEYS = ("results", "negatives", "events")
ID_RE = re.compile(r"EXP-(\d{6})\Z")
UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def canonical_line(record: dict) -> bytes:
    return (
        json.dumps(
            record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def normalize_eol(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n")


def parse_log_bytes(raw: bytes) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    if b"\r" in raw.replace(b"\r\n", b""):
        errors.append("ledger contains a bare CR byte")
    normalized = normalize_eol(raw)
    if normalized and not normalized.endswith(b"\n"):
        errors.append("ledger must end with LF")
    records: list[dict] = []
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
            errors.append(f"line {number}: record must be a JSON object")
            continue
        if line != canonical_line(record):
            errors.append(f"line {number}: non-canonical JSON encoding")
        records.append(record)
    return records, errors


def load_records(path: Path = LOG) -> tuple[list[dict], list[str], bytes]:
    raw = path.read_bytes() if path.exists() else b""
    records, errors = parse_log_bytes(raw)
    return records, errors, raw


def _unique_strings(value: object, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(f"{field}: expected a list of nonempty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{field}: duplicate values")
    return list(value)


def _known_references() -> dict[str, set[str]]:
    claims = {
        path.parent.name for path in (REPO / "claims").glob("*/status.json")
    }
    tasks_path = REPO / "todo" / "todo.json"
    tasks = {
        str(item.get("id", ""))
        for item in json.loads(tasks_path.read_text(encoding="utf-8")).get("tasks", [])
    }
    gate_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    gates = set(
        re.findall(
            r"^###\s+\*{0,2}([A-F]\d+[A-Z]?-[A-Z0-9][A-Z0-9-]{2,})\*{0,2}\s*$",
            gate_text,
            re.MULTILINE,
        )
    )
    result_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    results = set(re.findall(r"^###\s+(R-\d+)\b", result_text, re.MULTILINE))
    negative_text = (REPO / "negative-results" / "registry.md").read_text(
        encoding="utf-8"
    )
    negatives = set(
        re.findall(
            r"^###\s+((?:NG|AUDIT|R|F)-[A-Za-z0-9-]+)\b",
            negative_text,
            re.MULTILINE,
        )
    )
    event_path = REPO / "changelog" / "log.jsonl"
    events: set[str] = set()
    for line in event_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.add(str(json.loads(line).get("id", "")))
    return {
        "claims": claims,
        "tasks": tasks,
        "gates": gates,
        "results": results,
        "negatives": negatives,
        "events": events,
    }


def _validate_evidence_ref(value: str, prefix: str, errors: list[str]) -> None:
    path_text, _, locator = value.partition("#")
    candidate = Path(path_text)
    if not path_text or candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"{prefix}: evidence path must be repository-relative: {value!r}")
        return
    resolved = (REPO / candidate).resolve()
    try:
        resolved.relative_to(REPO.resolve())
    except ValueError:
        errors.append(f"{prefix}: evidence path escapes repository: {value!r}")
        return
    if not resolved.is_file():
        errors.append(f"{prefix}: missing evidence file: {path_text}")
    if not locator.strip():
        errors.append(f"{prefix}: evidence reference needs a section/line locator")


def validate_records(
    records: list[dict], known: dict[str, set[str]] | None = None
) -> list[str]:
    known = _known_references() if known is None else known
    errors: list[str] = []
    seen: set[str] = set()
    expected_number = 1
    previous_recorded_at = ""
    for index, record in enumerate(records, start=1):
        prefix = f"record {index}"
        if record.get("schema") != SCHEMA:
            errors.append(f"{prefix}: schema must be {SCHEMA}")
        identifier = str(record.get("id", ""))
        match = ID_RE.fullmatch(identifier)
        if not match:
            errors.append(f"{prefix}: invalid exploration id {identifier!r}")
        elif int(match.group(1)) != expected_number:
            errors.append(
                f"{prefix}: expected EXP-{expected_number:06d}, got {identifier}"
            )
        expected_number += 1
        if identifier in seen:
            errors.append(f"{prefix}: duplicate exploration id {identifier}")

        recorded_at = str(record.get("recorded_at", ""))
        if not UTC_RE.fullmatch(recorded_at):
            errors.append(f"{prefix}: recorded_at must be second-precision UTC")
        else:
            try:
                dt.datetime.strptime(recorded_at, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                errors.append(f"{prefix}: invalid recorded_at {recorded_at!r}")
            if previous_recorded_at and recorded_at < previous_recorded_at:
                errors.append(f"{prefix}: recorded_at must be append-order monotone")
            previous_recorded_at = recorded_at
        reviewed_on = str(record.get("reviewed_on", ""))
        try:
            dt.date.fromisoformat(reviewed_on)
        except ValueError:
            errors.append(f"{prefix}: reviewed_on must be an ISO date")

        if not isinstance(record.get("recorded_by"), str) or not str(
            record.get("recorded_by", "")
        ).strip():
            errors.append(f"{prefix}: recorded_by must be nonempty")
        if record.get("provenance") not in PROVENANCE:
            errors.append(f"{prefix}: invalid provenance {record.get('provenance')!r}")
        if record.get("verdict") not in VERDICTS:
            errors.append(f"{prefix}: invalid verdict {record.get('verdict')!r}")
        for field in CORE_TEXT:
            if not isinstance(record.get(field), str) or not str(
                record.get(field, "")
            ).strip():
                errors.append(f"{prefix}: {field} must be nonempty")

        methods = _unique_strings(record.get("method"), f"{prefix}.method", errors)
        if not methods:
            errors.append(f"{prefix}: at least one finite review method is required")
        claim_ids = _unique_strings(
            record.get("claim_ids"), f"{prefix}.claim_ids", errors
        )
        if not claim_ids:
            errors.append(f"{prefix}: at least one claim id is required")
        for claim in claim_ids:
            if claim not in known["claims"]:
                errors.append(f"{prefix}: unknown claim id {claim}")
        gate_ids = _unique_strings(
            record.get("gate_ids"), f"{prefix}.gate_ids", errors
        )
        for gate in gate_ids:
            if gate not in known["gates"]:
                errors.append(f"{prefix}: unknown gate id {gate}")
        task_id = record.get("task_id")
        if task_id is not None and task_id not in known["tasks"]:
            errors.append(f"{prefix}: unknown task id {task_id!r}")

        evidence = _unique_strings(
            record.get("evidence_refs"), f"{prefix}.evidence_refs", errors
        )
        if not evidence:
            errors.append(f"{prefix}: at least one evidence reference is required")
        for value in evidence:
            _validate_evidence_ref(value, prefix, errors)

        formal = record.get("formal_refs")
        if not isinstance(formal, dict) or set(formal) != set(FORMAL_KEYS):
            errors.append(f"{prefix}: formal_refs must contain exactly {FORMAL_KEYS}")
        else:
            for key in FORMAL_KEYS:
                values = _unique_strings(
                    formal.get(key), f"{prefix}.formal_refs.{key}", errors
                )
                for value in values:
                    if value not in known[key]:
                        errors.append(f"{prefix}: unknown formal {key[:-1]} {value}")

        related = record.get("related")
        if not isinstance(related, list):
            errors.append(f"{prefix}: related must be a list")
            related = []
        relation_pairs: set[tuple[str, str]] = set()
        for relation in related:
            if not isinstance(relation, dict) or set(relation) != {"id", "relation"}:
                errors.append(f"{prefix}: malformed related record {relation!r}")
                continue
            target = str(relation["id"])
            kind = str(relation["relation"])
            if kind not in RELATIONS:
                errors.append(f"{prefix}: invalid relation {kind!r}")
            if target not in seen:
                errors.append(f"{prefix}: related id must precede this record: {target}")
            pair = (target, kind)
            if pair in relation_pairs:
                errors.append(f"{prefix}: duplicate related edge {pair}")
            relation_pairs.add(pair)
        seen.add(identifier)
    return errors


def _find_git() -> str | None:
    configured = os.environ.get("TECT_GIT")
    if configured and Path(configured).is_file():
        return configured
    found = shutil.which("git")
    if found:
        return found
    runtime_root = Path.home() / ".cache" / "codex-runtimes"
    candidates = sorted(
        runtime_root.glob("*/dependencies/native/git/cmd/git.exe"),
        key=lambda path: ("primary" not in path.as_posix(), path.as_posix()),
    )
    return str(candidates[0]) if candidates else None


def head_bytes(git: str) -> tuple[bytes | None, str | None]:
    head = subprocess.run(
        [git, "rev-parse", "--verify", "HEAD"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if head.returncode != 0:
        return None, None
    exists = subprocess.run(
        [git, "cat-file", "-e", "HEAD:explorations/log.jsonl"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if exists.returncode != 0:
        return None, None
    shown = subprocess.run(
        [git, "show", "HEAD:explorations/log.jsonl"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if shown.returncode != 0:
        return None, shown.stderr.decode("utf-8", errors="replace").strip()
    return shown.stdout, None


def append_only_error(current: bytes, committed: bytes | None) -> str | None:
    if committed is None:
        return None
    if not normalize_eol(current).startswith(normalize_eol(committed)):
        return (
            "working ledger does not preserve git HEAD as a canonical-LF "
            "byte-identical prefix"
        )
    return None


def verify(path: Path = LOG, check_git: bool = True) -> tuple[list[dict], list[str]]:
    records, errors, raw = load_records(path)
    if not errors:
        errors.extend(validate_records(records))
    if check_git and path.resolve() == LOG.resolve():
        git = _find_git()
        if not git:
            errors.append("git executable unavailable; append-only HEAD check could not run")
        else:
            try:
                committed, git_error = head_bytes(git)
            except (OSError, subprocess.SubprocessError) as exc:
                errors.append(f"git append-only check failed: {exc}")
            else:
                if git_error:
                    errors.append(f"git append-only check failed: {git_error}")
                prefix_error = append_only_error(raw, committed)
                if prefix_error:
                    errors.append(prefix_error)
    return records, errors


def _now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _prepare_new_records(payload: object, existing: list[dict]) -> list[dict]:
    supplied = payload if isinstance(payload, list) else [payload]
    if not supplied or any(not isinstance(item, dict) for item in supplied):
        raise ValueError("input must be one record object or a nonempty record array")
    now = _now_utc()
    next_number = len(existing) + 1
    prepared: list[dict] = []
    for offset, item in enumerate(supplied):
        record = dict(item)
        expected_id = f"EXP-{next_number + offset:06d}"
        if record.get("id", expected_id) != expected_id:
            raise ValueError(f"next immutable id is {expected_id}")
        record["id"] = expected_id
        record.setdefault("schema", SCHEMA)
        record.setdefault("recorded_at", now)
        record.setdefault("recorded_by", "Codex")
        record.setdefault("reviewed_on", now[:10])
        record.setdefault("provenance", "contemporaneous")
        record.setdefault("gate_ids", [])
        record.setdefault("task_id", None)
        record.setdefault("related", [])
        record.setdefault("formal_refs", {key: [] for key in FORMAL_KEYS})
        prepared.append(record)
    return prepared


def cmd_add(path_text: str) -> int:
    existing, errors = verify()
    if errors:
        print("EXPLORATION-ADD: REFUSED; existing ledger failed integrity")
        for error in errors:
            print(f"  - {error}")
        return 1
    try:
        raw_input = sys.stdin.read() if path_text == "-" else Path(path_text).read_text(
            encoding="utf-8"
        )
        payload = json.loads(raw_input)
        new_records = _prepare_new_records(payload, existing)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"EXPLORATION-ADD: REFUSED; {exc}")
        return 1
    combined = existing + new_records
    validation = validate_records(combined)
    if validation:
        print("EXPLORATION-ADD: REFUSED; proposed records failed validation")
        for error in validation:
            print(f"  - {error}")
        return 1
    _, _, old_raw = load_records()
    use_crlf = bool(old_raw) and b"\r\n" in old_raw and b"\n" not in old_raw.replace(
        b"\r\n", b""
    )
    appended = b"".join(canonical_line(item) for item in new_records)
    if use_crlf:
        appended = appended.replace(b"\n", b"\r\n")
    atomic_write(LOG, old_raw + appended)
    print(
        f"EXPLORATION-ADD: appended {len(new_records)} record(s); "
        f"last id {new_records[-1]['id']}"
    )
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    records, errors = verify()
    if errors:
        for error in errors:
            print(f"EXPLORATION-VERIFY: FAIL - {error}")
        return 1
    matches = []
    for record in records:
        if args.claim and args.claim not in record["claim_ids"]:
            continue
        if args.gate and args.gate not in record["gate_ids"]:
            continue
        if args.verdict and args.verdict != record["verdict"]:
            continue
        if args.since and record["reviewed_on"] < args.since:
            continue
        haystack = json.dumps(record, ensure_ascii=False).lower()
        if args.text and args.text.lower() not in haystack:
            continue
        matches.append(record)
    if args.limit:
        matches = matches[-args.limit :]
    for record in matches:
        print(
            f"{record['id']} {record['reviewed_on']} [{record['verdict']}] "
            f"{record['title']}"
        )
        print(f"  {record['finding']}")
    print(f"EXPLORATION-SEARCH: {len(matches)} match(es)")
    return 0


def cmd_verify() -> int:
    records, errors = verify()
    if errors:
        print("EXPLORATION-VERIFY: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    counts = {verdict: sum(r["verdict"] == verdict for r in records) for verdict in VERDICTS}
    profile = ", ".join(f"{key}={value}" for key, value in counts.items())
    print(f"EXPLORATION-VERIFY: PASS ({len(records)} records; {profile})")
    return 0


def self_test() -> int:
    known = {
        "claims": {"A1-DEMO"},
        "tasks": {"T-001"},
        "gates": {"A1-DEMO-GATE"},
        "results": {"R-001"},
        "negatives": {"NG-2026-01-01-DEMO"},
        "events": {"20260101-demo"},
    }
    evidence = Path("GOVERNANCE.md")
    assert (REPO / evidence).exists()
    record = {
        "schema": SCHEMA,
        "id": "EXP-000001",
        "recorded_at": "2026-07-24T00:00:00Z",
        "recorded_by": "self-test",
        "reviewed_on": "2026-07-24",
        "provenance": "contemporaneous",
        "claim_ids": ["A1-DEMO"],
        "task_id": "T-001",
        "gate_ids": ["A1-DEMO-GATE"],
        "title": "Demo route",
        "question": "Does the demo route survive?",
        "method": ["Check the pinned finite identity."],
        "finding": "The scoped identity survives.",
        "verdict": "advanced",
        "decision_reason": "The exact check agrees.",
        "boundary": "This is not a theorem.",
        "next_action": "Test the next lemma.",
        "evidence_refs": ["GOVERNANCE.md#self-test-fixture"],
        "related": [],
        "formal_refs": {"results": ["R-001"], "negatives": [], "events": []},
    }
    assert not validate_records([record], known), "valid fixture rejected"
    raw = canonical_line(record)
    parsed, parse_errors = parse_log_bytes(raw)
    assert parsed == [record] and not parse_errors, "canonical round trip"
    assert append_only_error(raw + raw, raw) is None, "valid append rejected"
    assert append_only_error(raw.replace(b"Demo", b"Demu"), raw), "mutation accepted"
    broken = dict(record)
    broken["claim_ids"] = ["UNKNOWN"]
    assert validate_records([broken], known), "unknown reference accepted"
    print(
        "EXPLORATION-SELFTEST: PASS (schema, canonical JSON, references, "
        "append-only mutation guard)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TECT append-only proof exploration ledger")
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    add = sub.add_parser("add", help="append one record or a batch from JSON")
    add.add_argument("--file", required=True, help="JSON file path, or - for stdin")
    search = sub.add_parser("search", help="search verified exploration records")
    search.add_argument("--claim")
    search.add_argument("--gate")
    search.add_argument("--verdict", choices=VERDICTS)
    search.add_argument("--since")
    search.add_argument("--text")
    search.add_argument("--limit", type=int)
    sub.add_parser("verify", help="validate schema, references, and append-only history")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command == "add":
        return cmd_add(args.file)
    if args.command == "search":
        return cmd_search(args)
    if args.command == "verify":
        return cmd_verify()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
