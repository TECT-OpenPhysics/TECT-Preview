#!/usr/bin/env python3
"""Build a compact, reproducible extraction ledger for the frozen T-055 batch.

Only source identity, exact locators, registry links, and closure metadata are
stored.  The maintained Contents tree remains the byte source; this ledger
does not copy source text and never promotes a legacy calculation to proof.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
BATCH_DIR = (
    REPO
    / "archive"
    / "legacy"
    / "batches"
    / "LEGACY-T055-GEOMETRY-EMPTY-REFERENCE-001"
)
DEFAULT_MANIFEST = BATCH_DIR / "manifest.json"
DEFAULT_OUTPUT = BATCH_DIR / "source-extraction-ledger.json"
DEPENDENCY_FIELDS = ("dependencies", "dependency_paths", "dependency_source_ids")
RUN_FIELDS = ("run_paths", "run_refs", "result_ids")
HEADING_RE = re.compile(
    r"^\s*(?:#+\s+|%(?:\s*[-=]+)?\s*|\\(?:chapter|section|subsection|subsubsection|paragraph)\s*)"
)


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


def code_locators(data: bytes) -> list[dict]:
    text = data.decode("utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        locators = []
        for number, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^\s*(?:async\s+)?def\s+|^\s*class\s+", line):
                locators.append(
                    {"kind": "definition-line", "line": number, "text": line.strip()[:240]}
                )
        return locators[:64]
    locators = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            locators.append(
                {
                    "kind": kind,
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                }
            )
    return locators[:64]


def json_locators(data: bytes) -> list[dict]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    if isinstance(value, dict):
        return [
            {"kind": "top-level-key", "name": key}
            for key in sorted(str(key) for key in value)
        ][:64]
    if isinstance(value, list):
        return [{"kind": "top-level-array", "length": len(value)}]
    return [{"kind": "top-level-scalar", "type": type(value).__name__}]


def text_locators(data: bytes) -> list[dict]:
    text = data.decode("utf-8", errors="replace")
    locators = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or not HEADING_RE.match(line):
            continue
        locators.append(
            {"kind": "heading-line", "line": number, "text": stripped[:240]}
        )
        if len(locators) >= 64:
            break
    if not locators:
        for number, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                locators.append(
                    {"kind": "first-content-line", "line": number, "text": line.strip()[:240]}
                )
                break
    return locators


def extract_locators(origin: str, data: bytes) -> list[dict]:
    normalized = origin.replace("\\", "/").lower()
    if normalized.endswith(".py"):
        return code_locators(data)
    if normalized.endswith(".json"):
        return json_locators(data)
    return text_locators(data)


def load_records(selected_ids: set[str]) -> tuple[dict[str, list[dict]], list[dict]]:
    links: defaultdict[str, list[dict]] = defaultdict(list)
    records = []
    record_dir = REPO / "archive" / "legacy" / "registry" / "records"
    for record_path in sorted(record_dir.glob("*.json")):
        record = read_json(record_path)
        linked = set(record.get("source_ids", [])) & selected_ids
        if not linked:
            continue
        summary = {
            "record_id": str(record.get("record_id", "")),
            "path": record_path.relative_to(REPO).as_posix(),
            "evidence_role": record.get("evidence_role"),
            "current_assessment": record.get("current_assessment"),
            "status_axes": record.get("status_axes", {}),
        }
        records.append(summary)
        for source_id in sorted(linked):
            links[source_id].append(summary)
    return dict(links), records


def build_ledger(source_root: Path, manifest_path: Path, output_path: Path) -> dict:
    manifest = read_json(manifest_path)
    source_set_path = manifest_path.parent / "source-set.json"
    source_set = read_json(source_set_path)
    rows = list(source_set.get("sources", []))
    selected_ids = {str(row.get("source_id", "")) for row in rows}
    source_links, records = load_records(selected_ids)
    metadata_dir = REPO / "archive" / "legacy" / "registry" / "sources"

    errors: list[str] = []
    metadata_errors: list[str] = []
    identity_errors: list[str] = []
    entries: list[dict] = []
    counters: Counter[str] = Counter()

    digest_match = source_set.get("source_set_sha256") == canonical_source_set_digest(rows)
    if source_set.get("batch_id") != manifest.get("batch_id"):
        errors.append("manifest/source-set batch_id mismatch")
    if source_set.get("source_count") != len(rows):
        errors.append("source-set source_count mismatch")
    if len(selected_ids) != len(rows):
        errors.append("duplicate or empty source_id in source-set")
    if not digest_match:
        errors.append("source-set digest mismatch")

    for row in sorted(rows, key=lambda item: str(item.get("origin_path", ""))):
        source_id = str(row.get("source_id", ""))
        origin = str(row.get("origin_path", ""))
        source_path = source_root / origin
        metadata_path = metadata_dir / f"{source_id}.json"
        metadata = None
        if not metadata_path.is_file():
            metadata_errors.append(f"missing registry metadata: {source_id}")
        else:
            metadata = read_json(metadata_path)
        data = b""
        if not source_path.is_file():
            identity_errors.append(f"missing Contents source: {origin}")
        else:
            data = source_path.read_bytes()
            if len(data) != row.get("bytes"):
                identity_errors.append(f"byte count mismatch: {origin}")
            if sha256_bytes(data) != row.get("sha256"):
                identity_errors.append(f"sha256 mismatch: {origin}")
        if metadata is not None:
            if metadata.get("origin_path") != origin:
                identity_errors.append(f"registry origin mismatch: {source_id}")
            if metadata.get("bytes") != row.get("bytes"):
                identity_errors.append(f"registry byte count mismatch: {source_id}")
            if metadata.get("sha256") != row.get("sha256"):
                identity_errors.append(f"registry sha256 mismatch: {source_id}")

        dependency_fields = (
            [field for field in DEPENDENCY_FIELDS if metadata and bool(metadata.get(field))]
            if metadata is not None
            else []
        )
        run_fields = (
            [field for field in RUN_FIELDS if metadata and bool(metadata.get(field))]
            if metadata is not None
            else []
        )
        normalized_origin = origin.replace("\\", "/")
        run_origin = normalized_origin.startswith("Runs/")
        linked_records = source_links.get(source_id, [])
        statuses = sorted(
            {
                str((record.get("status_axes") or {}).get("revalidation", "missing"))
                for record in linked_records
            }
        )
        locators = extract_locators(origin, data) if data else []
        if not locators:
            counters["no_locator"] += 1
        else:
            counters["locator_present"] += 1
        if dependency_fields:
            counters["dependency_declared"] += 1
        if run_origin:
            counters["run_origin"] += 1
            if run_fields:
                counters["run_declared"] += 1
        if not linked_records:
            counters["unlinked_source"] += 1
        if any(status != "pass" for status in statuses):
            counters["revalidation_open_source"] += 1
        else:
            counters["revalidation_pass_source"] += 1
        if not dependency_fields or (run_origin and not run_fields):
            readiness = "NOT_READY_MISSING_CLOSURE_LINK"
        elif any(status != "pass" for status in statuses):
            readiness = "NOT_READY_REVALIDATION_OPEN"
        else:
            readiness = "READY_FOR_METHOD_REVIEW"
        counters[f"source_kind:{str((metadata or {}).get('source_kind', 'missing'))}"] += 1
        counters[f"readiness:{readiness}"] += 1
        entries.append(
            {
                "source_id": source_id,
                "origin_path": origin,
                "sha256": row.get("sha256"),
                "bytes": row.get("bytes"),
                "source_kind": (metadata or {}).get("source_kind"),
                "canonicality": (metadata or {}).get("canonicality"),
                "copy_encoding": (metadata or {}).get("copy_encoding"),
                "compatibility_paths": (metadata or {}).get("compatibility_paths", []),
                "record_links": [
                    {
                        "record_id": record["record_id"],
                        "path": record["path"],
                        "evidence_role": record["evidence_role"],
                        "current_assessment": record["current_assessment"],
                        "revalidation": (record.get("status_axes") or {}).get("revalidation"),
                    }
                    for record in linked_records
                ],
                "revalidation_statuses": statuses,
                "extraction_locators": locators,
                "dependency_fields_declared": dependency_fields,
                "run_fields_declared": run_fields,
                "run_origin": run_origin,
                "execution_link_status": (
                    "DECLARED" if run_fields else "MISSING_EXPLICIT_EXECUTION_LINK"
                    if run_origin
                    else "NOT_DECLARED"
                ),
                "readiness": readiness,
            }
        )

    linked_ids = set(source_links)
    checks = {
        "manifest_source_set_consistent": not errors,
        "source_set_digest_match": digest_match,
        "selected_identity_hashes_match": not identity_errors,
        "registry_metadata_present": not metadata_errors,
        "record_links_cover_selection": linked_ids == selected_ids,
        "all_sources_have_exact_locators": counters["no_locator"] == 0,
        "dependency_closure_complete": counters["dependency_declared"] == len(rows),
        "run_closure_complete_for_run_origins": counters["run_declared"] == counters["run_origin"],
        "all_linked_records_revalidated": counters["revalidation_open_source"] == 0,
    }
    if not checks["record_links_cover_selection"]:
        errors.append("record links do not cover every selected source")
    contract_status = (
        "EXTRACTION_LEDGER_READY_CLOSURE_OPEN"
        if not errors and not metadata_errors and not identity_errors
        and checks["record_links_cover_selection"]
        else "AUDIT_INPUT_OR_IDENTITY_FAIL"
    )
    result = {
        "schema_version": "tect/t057-source-extraction-ledger/1.0",
        "batch_id": manifest.get("batch_id"),
        "task_id": manifest.get("task_id"),
        "source_root_label": source_root.name,
        "manifest_path": manifest_path.relative_to(REPO).as_posix(),
        "source_set_path": source_set_path.relative_to(REPO).as_posix(),
        "generated_by": "verification/scripts/t057_source_extraction_ledger.py",
        "scope": "T0 compact per-source extraction, locator, registry-link, and closure ledger",
        "contract_status": contract_status,
        "counts": {
            "selected_sources": len(rows),
            "entries": len(entries),
            "linked_records": len(records),
            "linked_sources": len(linked_ids),
            "unlinked_sources": len(selected_ids - linked_ids),
            "sources_with_locators": counters["locator_present"],
            "sources_without_locators": counters["no_locator"],
            "dependency_declarations": counters["dependency_declared"],
            "run_origin_sources": counters["run_origin"],
            "run_declarations": counters["run_declared"],
            "sources_with_open_revalidation": counters["revalidation_open_source"],
            "sources_with_revalidation_pass": counters["revalidation_pass_source"],
        },
        "derived_buckets": {
            key: value for key, value in sorted(counters.items())
            if key not in {
                "locator_present",
                "no_locator",
                "dependency_declared",
                "run_origin",
                "run_declared",
                "unlinked_source",
                "revalidation_open_source",
                "revalidation_pass_source",
            }
        },
        "checks": checks,
        "assertions": [
            {"name": name, "passed": passed} for name, passed in checks.items()
        ],
        "errors": errors + metadata_errors + identity_errors,
        "entries": entries,
        "assumptions": [
            "Contents is the canonical byte source and the frozen source-set defines selection.",
            "AST, top-level JSON keys, and heading lines are locators only; they do not validate mathematics.",
            "A missing dependency or execution link remains missing even when a filename or record suggests one.",
        ],
        "missing_assumptions": [
            "Per-source dependency closure and reproducible import/input graph.",
            "Explicit run-to-script, input, output, and result-status links for run-origin sources.",
            "Current-convention functional, normalization, sign, competitor, stability, error, and ordered-limit reruns.",
        ],
        "non_claims": [
            "No legacy statement is revalidated or promoted by this index.",
            "No BCC, truncated-octahedron, Reading-H, physical-empty, C6, Pre-A, Sector-A, QFT, Yang--Mills, continuum, or mass-gap conclusion.",
            "No source text is copied into the ledger; Contents remains the live source.",
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
    result = build_ledger(
        args.source_root.resolve(), args.manifest.resolve(), args.output.resolve()
    )
    counts = result["counts"]
    print(
        "T057-SOURCE-EXTRACTION-LEDGER: "
        f"{result['contract_status']} "
        f"(entries={counts['entries']}; locators={counts['sources_with_locators']}; "
        f"dependency_declarations={counts['dependency_declarations']}; "
        f"run_sources={counts['run_origin_sources']}; "
        f"run_declarations={counts['run_declarations']}; "
        f"open_revalidation={counts['sources_with_open_revalidation']})"
    )
    if args.self_test:
        assert result["checks"]["manifest_source_set_consistent"]
        assert result["checks"]["source_set_digest_match"]
        assert result["checks"]["selected_identity_hashes_match"]
        assert result["checks"]["registry_metadata_present"]
        assert result["checks"]["record_links_cover_selection"]
        assert result["checks"]["all_sources_have_exact_locators"]
        assert result["contract_status"] == "EXTRACTION_LEDGER_READY_CLOSURE_OPEN"
        print("T057-SOURCE-EXTRACTION-LEDGER SELFTEST: PASS")
    return 0 if result["contract_status"] != "AUDIT_INPUT_OR_IDENTITY_FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
