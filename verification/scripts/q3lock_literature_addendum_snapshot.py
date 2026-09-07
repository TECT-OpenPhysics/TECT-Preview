#!/usr/bin/env python3
"""Snapshot a documentation-only QPS comparison without rewriting old runs.

This checks provenance and replays existing diagnostics. It cannot validate
source interpretation, theorem applicability, novelty, or external acceptance.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PAPER = "publish/papers/q3lock-phase-coexistence/"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_source_audit.py"
HISTORICAL = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-manuscript-source-audit/result.json"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-literature-qps-addendum/result.json"
ALLOWED_DOCUMENTS = frozenset(PAPER + name for name in (
    "README.md", "external-review-handoff.md", "literature-qps-addendum.md"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def differences(old, new, path=""):
    if isinstance(old, dict) and isinstance(new, dict):
        return [row for key in sorted(old.keys() | new.keys())
                for row in differences(old.get(key), new.get(key), path + "/" + key)]
    return [] if old == new else [{"path": path, "old": old, "new": new}]


def build_payload():
    before = HISTORICAL.read_bytes()
    old = json.loads(before)
    current = runpy.run_path(str(PRIOR), run_name="q3lock_source_readonly")["build_payload"]()
    changes = differences(old, current)
    # Compare the entire nested payload, not just the top source hash list.
    # All prior diagnostics and frozen authority checks must remain identical.
    assert changes, "The documentation checkpoint must have explicit provenance changes."
    for row in changes:
        prefix, separator, source = row["path"].rpartition("/source_hashes/")
        assert separator and source in ALLOWED_DOCUMENTS, row
        assert row["new"] == digest(ROOT / source), row
    assert {row["path"].rpartition("/source_hashes/")[2] for row in changes} == ALLOWED_DOCUMENTS
    assert HISTORICAL.read_bytes() == before, "Historical source audit must not be overwritten."
    return {
        "schema": "tect/q3lock-literature-addendum-snapshot/1.0",
        "status": "PASS", "claim_bearing": False,
        "scope": "Documentation provenance and unchanged diagnostic replay only; no analytic, literature or novelty certification.",
        "manuscript_version": "0.1.7", "pdf_status": "DEFERRED",
        "historical_run_sha256": hashlib.sha256(before).hexdigest(),
        "allowed_document_changes": changes,
        "source_hashes": {path: digest(ROOT/path) for path in sorted(
            ALLOWED_DOCUMENTS | {Path(__file__).resolve().relative_to(ROOT).as_posix()})},
        "current_manuscript_diagnostics": current,
    }


if __name__ == "__main__":
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Q3LOCK literature addendum snapshot: PASS; prior diagnostics unchanged;")
    print(f"documentation provenance changes: {len(payload['allowed_document_changes'])}; historical run preserved")
    print(OUT.relative_to(ROOT).as_posix())
