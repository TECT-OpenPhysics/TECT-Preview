"""Integrity tests for the append-only proof-exploration ledger."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "verification" / "scripts" / "exploration.py"
LOG = REPO / "explorations" / "log.jsonl"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_exploration_ledger_verifies():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "EXPLORATION-VERIFY: PASS" in result.stdout


def test_log_is_canonical_sequential_jsonl():
    module = load_module(SCRIPT, "tect_exploration_canonical")
    raw = LOG.read_bytes()
    records, errors = module.parse_log_bytes(raw)
    assert not errors
    assert records
    assert [record["id"] for record in records] == [
        f"EXP-{number:06d}" for number in range(1, len(records) + 1)
    ]
    assert raw == b"".join(module.canonical_line(record) for record in records)


def test_append_only_prefix_guard_rejects_mutation_deletion_and_reorder():
    module = load_module(SCRIPT, "tect_exploration_prefix")
    committed = b'{"id":"EXP-000001"}\n'
    appended = committed + b'{"id":"EXP-000002"}\n'
    assert module.append_only_error(appended, committed) is None
    assert module.append_only_error(b'{"id":"EXP-999999"}\n', committed)
    assert module.append_only_error(b"", committed)
    assert module.append_only_error(appended[len(committed) :] + committed, committed)
    assert module.append_only_error(committed.replace(b"\n", b"\r\n"), committed) is None


def test_schema_rejects_unknown_refs_and_path_escape(tmp_path, monkeypatch):
    module = load_module(SCRIPT, "tect_exploration_schema")
    monkeypatch.setattr(module, "REPO", tmp_path)
    (tmp_path / "evidence.md").write_text("fixture\n", encoding="utf-8")
    known = {
        "claims": {"A1-DEMO"},
        "tasks": {"T-001"},
        "gates": {"A1-DEMO-GATE"},
        "results": set(),
        "negatives": set(),
        "events": set(),
    }
    record = {
        "schema": module.SCHEMA,
        "id": "EXP-000001",
        "recorded_at": "2026-07-24T00:00:00Z",
        "recorded_by": "test",
        "reviewed_on": "2026-07-24",
        "provenance": "contemporaneous",
        "claim_ids": ["A1-DEMO"],
        "task_id": "T-001",
        "gate_ids": ["A1-DEMO-GATE"],
        "title": "Fixture",
        "question": "Does the fixture survive?",
        "method": ["Run a finite check."],
        "finding": "The fixture is scoped.",
        "verdict": "inconclusive",
        "decision_reason": "One discriminator is missing.",
        "boundary": "No proof is claimed.",
        "next_action": "Supply the missing discriminator.",
        "evidence_refs": ["evidence.md#fixture"],
        "related": [],
        "formal_refs": {"results": [], "negatives": [], "events": []},
    }
    assert not module.validate_records([record], known)

    unknown = json.loads(json.dumps(record))
    unknown["claim_ids"] = ["A1-UNKNOWN"]
    assert any("unknown claim" in error for error in module.validate_records([unknown], known))

    escaped = json.loads(json.dumps(record))
    escaped["evidence_refs"] = ["../outside.md#fixture"]
    assert any("repository-relative" in error for error in module.validate_records([escaped], known))


def test_related_edges_must_point_backward(tmp_path, monkeypatch):
    module = load_module(SCRIPT, "tect_exploration_related")
    monkeypatch.setattr(module, "REPO", tmp_path)
    (tmp_path / "evidence.md").write_text("fixture\n", encoding="utf-8")
    known = {
        "claims": {"A1-DEMO"},
        "tasks": set(),
        "gates": set(),
        "results": set(),
        "negatives": set(),
        "events": set(),
    }
    base = {
        "schema": module.SCHEMA,
        "recorded_at": "2026-07-24T00:00:00Z",
        "recorded_by": "test",
        "reviewed_on": "2026-07-24",
        "provenance": "contemporaneous",
        "claim_ids": ["A1-DEMO"],
        "task_id": None,
        "gate_ids": [],
        "title": "Fixture",
        "question": "Question?",
        "method": ["Check."],
        "finding": "Finding.",
        "verdict": "advanced",
        "decision_reason": "Reason.",
        "boundary": "Boundary.",
        "next_action": "Next.",
        "evidence_refs": ["evidence.md#fixture"],
        "formal_refs": {"results": [], "negatives": [], "events": []},
    }
    first = dict(base, id="EXP-000001", related=[])
    second = dict(
        base,
        id="EXP-000002",
        related=[{"id": "EXP-000001", "relation": "continues"}],
    )
    assert not module.validate_records([first, second], known)
    first["related"] = [{"id": "EXP-000002", "relation": "continues"}]
    assert any(
        "must precede" in error for error in module.validate_records([first, second], known)
    )
