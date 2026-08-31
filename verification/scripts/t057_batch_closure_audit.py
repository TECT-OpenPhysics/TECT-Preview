#!/usr/bin/env python3
"""Audit the frozen T-055 batch without importing it as proof authority.

The audit is deliberately narrower than a mathematical revalidation.  It
checks byte/hash identity, source-set integrity, registry-record coverage, and
whether per-source dependency/run declarations exist.  A preservation PASS
with missing closure metadata is an honest open boundary, not a gate closure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    REPO
    / "archive"
    / "legacy"
    / "batches"
    / "LEGACY-T055-GEOMETRY-EMPTY-REFERENCE-001"
    / "manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "C6-SPACETIME-SIGNATURE"
    / "runs"
    / "2026-08-31-t057-batch-closure-audit"
    / "primary.json"
)
DEPENDENCY_FIELDS = ("dependencies", "dependency_paths", "dependency_source_ids")
RUN_FIELDS = ("run_paths", "run_refs", "result_ids")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_source_set_digest(rows: list[dict]) -> str:
    payload = "\n".join(
        f"{row['origin_path']}:{row['sha256']}" for row in rows
    ).encode("utf-8")
    return sha256_bytes(payload)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def audit(source_root: Path, manifest_path: Path, output_path: Path) -> dict:
    manifest = read_json(manifest_path)
    source_set_path = manifest_path.parent / "source-set.json"
    source_set = read_json(source_set_path)
    rows = list(source_set.get("sources", []))
    source_ids = [row.get("source_id") for row in rows]
    origins = [row.get("origin_path") for row in rows]
    errors: list[str] = []

    if source_set.get("batch_id") != manifest.get("batch_id"):
        errors.append("manifest/source-set batch_id mismatch")
    if source_set.get("source_count") != len(rows):
        errors.append("source-set source_count mismatch")
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source_id in source-set")
    if len(origins) != len(set(origins)):
        errors.append("duplicate origin_path in source-set")
    digest_match = source_set.get("source_set_sha256") == canonical_source_set_digest(rows)
    if not digest_match:
        errors.append("source-set digest mismatch")

    metadata_by_id: dict[str, dict] = {}
    metadata_errors: list[str] = []
    identity_errors: list[str] = []
    dependency_declared = 0
    run_declared = 0
    run_origin_count = 0
    source_record_links: defaultdict[str, list[str]] = defaultdict(list)

    record_dir = REPO / "archive" / "legacy" / "registry" / "records"
    records: list[dict] = []
    for record_path in sorted(record_dir.glob("*.json")):
        record = read_json(record_path)
        linked = set(record.get("source_ids", [])) & set(source_ids)
        if linked:
            records.append(record)
            for source_id in linked:
                source_record_links[source_id].append(str(record.get("record_id", "")))

    for row in rows:
        source_id = str(row.get("source_id", ""))
        origin = str(row.get("origin_path", ""))
        metadata_path = REPO / "archive" / "legacy" / "registry" / "sources" / f"{source_id}.json"
        if not metadata_path.is_file():
            metadata_errors.append(f"missing registry metadata: {source_id}")
            continue
        metadata = read_json(metadata_path)
        metadata_by_id[source_id] = metadata
        if metadata.get("origin_path") != origin:
            identity_errors.append(f"origin mismatch: {source_id}")
        source_path = source_root / origin
        if not source_path.is_file():
            identity_errors.append(f"missing Contents source: {origin}")
        else:
            data = source_path.read_bytes()
            if len(data) != row.get("bytes"):
                identity_errors.append(f"byte count mismatch: {origin}")
            if sha256_bytes(data) != row.get("sha256"):
                identity_errors.append(f"sha256 mismatch: {origin}")
        if metadata.get("sha256") != row.get("sha256"):
            identity_errors.append(f"registry hash mismatch: {source_id}")
        if metadata.get("bytes") != row.get("bytes"):
            identity_errors.append(f"registry byte count mismatch: {source_id}")
        if any(bool(metadata.get(field)) for field in DEPENDENCY_FIELDS):
            dependency_declared += 1
        is_run_origin = origin.replace("\\", "/").startswith("Runs/")
        if is_run_origin:
            run_origin_count += 1
            if any(bool(metadata.get(field)) for field in RUN_FIELDS):
                run_declared += 1

    linked_ids = set(source_record_links)
    unlinked_ids = sorted(set(source_ids) - linked_ids)
    revalidation = Counter(
        str((record.get("status_axes") or {}).get("revalidation", "missing"))
        for record in records
    )
    run_reference_root = REPO / "archive" / "legacy" / "references" / "Runs"
    archived_runs = sorted(
        path.relative_to(run_reference_root).as_posix()
        for path in run_reference_root.rglob("*")
        if path.is_file()
    )
    closure_open = bool(
        metadata_errors
        or dependency_declared < len(rows)
        or run_declared < run_origin_count
        or any(value != "pass" for value in revalidation)
    )
    checks = {
        "manifest_source_set_consistent": not errors,
        "source_set_digest_match": digest_match,
        "selected_identity_hashes_match": not identity_errors,
        "registry_metadata_present": not metadata_errors,
        "record_links_cover_selection": not unlinked_ids,
        "dependency_closure_declared_per_source": dependency_declared == len(rows),
        "run_closure_declared_for_run_sources": run_declared == run_origin_count,
        "revalidation_complete_for_linked_records": all(
            value == "pass" for value in revalidation
        ),
    }
    contract_status = (
        "PRESERVATION_PASS_CLOSURE_OPEN" if not errors and not identity_errors and closure_open
        else "PRESERVATION_AND_CLOSURE_PASS"
        if not errors and not identity_errors and not closure_open
        else "AUDIT_INPUT_OR_IDENTITY_FAIL"
    )
    result = {
        "schema_version": "tect/t057-batch-closure-audit/1.0",
        "batch_id": manifest.get("batch_id"),
        "task_id": manifest.get("task_id"),
        "source_root_label": source_root.name,
        "manifest_path": manifest_path.relative_to(REPO).as_posix(),
        "source_set_path": source_set_path.relative_to(REPO).as_posix(),
        "scope": "T0 hash, registry-link, and dependency/run-closure metadata audit",
        "contract_status": contract_status,
        "counts": {
            "selected_sources": len(rows),
            "registry_metadata_rows": len(metadata_by_id),
            "linked_sources": len(linked_ids),
            "unlinked_sources": len(unlinked_ids),
            "dependency_declarations": dependency_declared,
            "run_origin_sources": run_origin_count,
            "run_declarations": run_declared,
            "linked_records": len(records),
            "archived_run_files": len(archived_runs),
        },
        "revalidation_status": dict(sorted(revalidation.items())),
        "archived_run_files": archived_runs,
        "unlinked_source_ids": unlinked_ids,
        "errors": errors + metadata_errors + identity_errors,
        "checks": checks,
        "assertions": [
            {"name": name, "passed": passed} for name, passed in checks.items()
        ],
        "assumptions": [
            "The maintained Contents tree is the canonical byte source for this batch.",
            "Registry source IDs and the frozen source-set are the repository provenance contract.",
            "A metadata or run-link absence is reported as an open closure field, not inferred from filenames.",
        ],
        "missing_assumptions": [
            "Per-source dependency paths or dependency source IDs with a reproducible closure.",
            "Per-run source-to-artifact/result links and current-convention execution records.",
            "Current-kernel normalization, sign, competitor, stability, error, and ordered-limit reruns.",
        ],
        "non_claims": [
            "No BCC selection, truncated-octahedron physical realization, or Reading-H sign.",
            "No physical-empty, Pre-A, Sector-A, C6, QFT, Yang--Mills, continuum, or mass-gap conclusion.",
            "No source is promoted from discovery or intake status by this audit.",
        ],
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    atomic_json(output_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(
        args.source_root.resolve(), args.manifest.resolve(), args.output.resolve()
    )
    counts = result["counts"]
    print(
        "T057-BATCH-CLOSURE-AUDIT: "
        f"{result['contract_status']} "
        f"(selected={counts['selected_sources']}; "
        f"identity_errors={len(result['errors'])}; "
        f"dependency_declarations={counts['dependency_declarations']}; "
        f"run_sources={counts['run_origin_sources']}; "
        f"run_declarations={counts['run_declarations']}; "
        f"linked_records={counts['linked_records']})"
    )
    if args.self_test:
        assert result["checks"]["manifest_source_set_consistent"]
        assert result["checks"]["source_set_digest_match"]
        assert result["checks"]["selected_identity_hashes_match"]
        assert result["checks"]["registry_metadata_present"]
        assert result["checks"]["record_links_cover_selection"]
        assert result["contract_status"] == "PRESERVATION_PASS_CLOSURE_OPEN"
        print("T057-BATCH-CLOSURE-AUDIT SELFTEST: PASS")
    return 0 if result["contract_status"] != "AUDIT_INPUT_OR_IDENTITY_FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
