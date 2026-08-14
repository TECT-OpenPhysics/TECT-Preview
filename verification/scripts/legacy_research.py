#!/usr/bin/env python3
"""Preserve, index, validate, and render selected TECT legacy references.

Commands:
  backfill-existing --source-root PATH
      Index the existing immutable archive payloads against byte-identical
      Contents sources without copying another raw-object layer.
  ingest-batch --source-root PATH --manifest FILE
      Resolve a gate-linked batch manifest, preserve newly selected important
      sources at readable reference paths, and write an exact source set.
  verify-external --source-root PATH
      Verify every selected Contents reference against its pinned size/hash.
  pin-records
      Replace tag discovery by an explicit immutable source-ID set for records
      that have not yet been pinned.
  build [--check]
      Validate source and research records and render all generated views.

Contents remains the maintained full corpus. Selected preservation never
promotes a claim.
"""

__version__ = "1.2.0"
__first_issued__ = "2026-08-14"
__version_issued__ = "2026-08-14"

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LEGACY = REPO / "archive" / "legacy"
REGISTRY = LEGACY / "registry"
SOURCE_DIR = REGISTRY / "sources"
RECORD_DIR = REGISTRY / "records"
REFERENCE_ROOT = LEGACY / "references"
CONTENTS_REFERENCE_MD = LEGACY / "CONTENTS-REFERENCE.md"
RESEARCH_INDEX_MD = LEGACY / "RESEARCH-INDEX.md"
VIEW_ROOT = LEGACY / "views"
MACHINE_INDEX = REPO / "verification" / "legacy-research-index.json"
SNAPSHOT_ID = "TECT-CONTENTS-SELECTED-2026-08-14"
SCHEMA_VERSION = "1.0.0"

SECTORS = {
    "A": "Microscopic Foundation",
    "B": "Vacuum / Reading Selection",
    "C": "Spacetime / Lorentz / Gravity",
    "D": "Gauge / Matter / Topology",
    "E": "Spectrum / Couplings / Constants",
    "F": "Cosmology / Falsifiability",
}
ASSESSMENTS = {
    "unreviewed", "reusable", "revalidate-required", "partially-reusable",
    "superseded", "refuted", "context-only",
}
EVIDENCE_ROLES = {
    "candidate-support", "counterevidence", "method", "provenance",
    "negative-control", "dependency", "context",
}
CANONICALITIES = {
    "CANONICAL_RAW", "DUPLICATE_ALIAS", "GENERATED_DERIVATIVE",
    "VCS_METADATA", "EXTERNAL_REFERENCE", "BUILD_NOISE",
}
STORAGE_CLASSES = {"compatibility-copy", "reference-copy", "contents-reference"}
COPY_ENCODINGS = {"raw", "base64-json", "none"}
AXIS_VALUES = {
    "preservation": {"inventoried", "verified-copy", "missing"},
    "extraction": {"pending", "reviewed", "needs-review"},
    "revalidation": {"not-run", "pass", "fail", "waived", "not-applicable"},
    "integration": {"unmapped", "mapped", "candidate", "integrated", "terminal"},
}
TAG_RE = re.compile(r"Math(?:_|-)?([0-9]+)", re.IGNORECASE)
HANGUL_RE = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]")


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def text_contains_hangul(data: bytes) -> bool:
    for encoding in ("utf-8", "cp949"):
        try:
            return bool(HANGUL_RE.search(data.decode(encoding)))
        except UnicodeDecodeError:
            continue
    return False


def reference_target(origin: str, data: bytes):
    if text_contains_hangul(data):
        return REFERENCE_ROOT / f"{origin}.source.json", "base64-json"
    return REFERENCE_ROOT / origin, "raw"


def write_reference_copy(origin: str, data: bytes):
    target, encoding = reference_target(origin, data)
    if encoding == "raw":
        expected = data
    else:
        expected = canonical_json({
            "schema_version": "1.0.0",
            "encoding": "base64",
            "origin_path": origin,
            "sha256": sha_bytes(data),
            "bytes": len(data),
            "payload_base64": base64.b64encode(data).decode("ascii"),
        }).encode("utf-8")
    if target.exists() and target.read_bytes() != expected:
        raise ValueError(f"reference copy changed: {rel(target)}")
    if not target.exists():
        atomic_write_bytes(target, expected)
    return target, encoding


def preserved_copy_bytes(item, path: Path) -> bytes:
    encoding = item.get("copy_encoding", "raw")
    if encoding == "raw":
        return path.read_bytes()
    if encoding != "base64-json":
        raise ValueError(f"{item['source_id']}: unsupported copy encoding {encoding}")
    wrapper = load_json(path)
    if wrapper.get("origin_path") != item["origin_path"]:
        raise ValueError(f"{item['source_id']}: wrapper origin mismatch")
    try:
        return base64.b64decode(wrapper["payload_base64"], validate=True)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{item['source_id']}: invalid base64 wrapper") from exc


def source_id(origin_path: str) -> str:
    digest = hashlib.sha256(origin_path.encode("utf-8")).hexdigest()[:16].upper()
    return f"LEG-SRC-{digest}"


def tags_for(*values: str) -> list[str]:
    found = set()
    for value in values:
        if "Math_IR_Bound" in value:
            found.add("MathIRBound")
        for match in TAG_RE.finditer(value):
            found.add(f"Math{int(match.group(1)):02d}")
    return sorted(found)


def source_kind(path: Path) -> str:
    p = path.as_posix()
    if "/notes/" in p:
        return "note"
    if "/scripts/" in p:
        return "script"
    if "/artefacts/" in p:
        return "artefact"
    return "other"


def origin_source_kind(origin: str) -> str:
    if origin.startswith("Docs/math/"):
        return "note"
    if origin.startswith("Codes/"):
        return "script"
    if origin.startswith("Runs/"):
        return "artefact"
    if origin.startswith("Docs/status/"):
        return "status"
    if origin.startswith("Docs/papers/"):
        return "reference"
    return "other"


def migration_batch(tags: list[str]) -> str:
    numbers = {int(t[4:]) for t in tags}
    if numbers & {374, 400, 424, 426, 435, 437, 440, 441, 442}:
        return "legacy-batch-1"
    if numbers & {427, 428, 429, 430, 431, 432, 434, 436}:
        return "legacy-batch-2"
    if numbers & {1, 56, 82}:
        return "legacy-batch-3"
    if numbers & {194, 383}:
        return "legacy-batch-4"
    return "legacy-pre-cutover"


def exact_origin_candidates(source_root: Path, payloads: list[Path]) -> dict[str, list[str]]:
    by_name_size: dict[tuple[str, int], list[Path]] = defaultdict(list)
    by_size: dict[int, list[Path]] = defaultdict(list)
    for path in source_root.rglob("*"):
        if path.is_file():
            by_name_size[(path.name, path.stat().st_size)].append(path)
            by_size[path.stat().st_size].append(path)
    result = {}
    digest_cache = {}
    for payload in payloads:
        digest = sha_file(payload)
        candidates = []
        pool = by_name_size[(payload.name, payload.stat().st_size)]
        if not pool:
            # Some early archive payloads received a descriptive compatibility
            # filename (for example a generic source MANIFEST.md). Full hash is
            # authoritative, so fall back to same-size candidates.
            pool = by_size[payload.stat().st_size]
        for candidate in pool:
            key = str(candidate)
            candidate_digest = digest_cache.get(key)
            if candidate_digest is None:
                candidate_digest = sha_file(candidate)
                digest_cache[key] = candidate_digest
            if candidate_digest == digest:
                candidates.append(candidate.relative_to(source_root).as_posix())
        result[rel(payload)] = sorted(candidates, key=origin_priority)
    return result


def origin_priority(path: str):
    if path.startswith("Docs/math/"):
        rank = 0
    elif path.startswith("Codes/"):
        rank = 1
    elif path.startswith("Runs/"):
        rank = 2
    elif path.startswith("Docs/"):
        rank = 3
    elif path.startswith("Backup/"):
        rank = 7
    elif path.startswith("Github/"):
        rank = 8
    elif path.startswith("Website/"):
        rank = 9
    else:
        rank = 5
    return (rank, len(path), path)


def backfill_existing(source_root: Path) -> int:
    payloads = sorted(
        path for folder in (LEGACY / "notes", LEGACY / "scripts", LEGACY / "artefacts")
        for path in folder.rglob("*") if path.is_file()
    )
    candidates = exact_origin_candidates(source_root, payloads)
    errors = []
    records = []
    for payload in payloads:
        compat = rel(payload)
        origins = candidates[compat]
        if not origins:
            errors.append(f"no byte-identical Contents source: {compat}")
            continue
        origin = origins[0]
        data = payload.read_bytes()
        digest = sha_bytes(data)
        tags = tags_for(compat, origin)
        disposition = "SUPERSEDED" if any(t in {"Math194", "Math383"} for t in tags) else "MIGRATED-VERBATIM"
        item = {
            "schema_version": SCHEMA_VERSION,
            "source_id": source_id(origin),
            "snapshot_id": SNAPSHOT_ID,
            "origin_path": origin,
            "origin_candidates": origins,
            "sha256": digest,
            "bytes": len(data),
            "compatibility_paths": [compat],
            "source_kind": source_kind(payload),
            "canonicality": "CANONICAL_RAW",
            "storage_class": "compatibility-copy",
            "source_location": "compatibility-copy",
            "copy_encoding": "raw",
            "preservation": "verified-copy",
            "theory_tags": tags,
            "ingested_on": "2026-08-14",
            "migration_batch": migration_batch(tags),
            "legacy_disposition": disposition,
        }
        records.append(item)
    ids = [item["source_id"] for item in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate source IDs after origin-path selection")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for item in records:
        path = SOURCE_DIR / f"{item['source_id']}.json"
        atomic_write_text(path, canonical_json(item))
    print(f"LEGACY-BACKFILL: PASS ({len(records)} compatibility sources indexed)")
    return 0


def pin_records() -> int:
    sources = load_sources()
    by_tag = defaultdict(list)
    for source in sources:
        for tag in source.get("theory_tags", []):
            by_tag[tag].append(source["source_id"])
    changed = 0
    for path in sorted(RECORD_DIR.glob("*.json")):
        item = load_json(path)
        if "source_ids" in item:
            continue
        selected = sorted({sid for tag in item["source_tags"] for sid in by_tag[tag]})
        if not selected:
            print(f"[FAIL] no sources available to pin {item['record_id']}")
            return 1
        item["source_ids"] = selected
        digest_input = "\n".join(selected)
        item["pinned_source_ids_sha256"] = sha_bytes(digest_input.encode("utf-8"))
        atomic_write_text(path, canonical_json(item))
        changed += 1
    print(f"LEGACY-PIN-RECORDS: PASS ({changed} records newly pinned)")
    return 0


def ingest_batch(source_root: Path, manifest_path: Path) -> int:
    manifest = load_json(manifest_path)
    required = {"schema_version", "batch_id", "task_id", "claim_ids", "gate_ids", "questions", "source_globs", "boundary"}
    missing = sorted(required - manifest.keys())
    if missing:
        print(f"[FAIL] batch manifest missing {missing}")
        return 1
    selected = {}
    for pattern in manifest["source_globs"]:
        for path in source_root.glob(pattern):
            if path.is_file():
                selected[path.relative_to(source_root).as_posix()] = path
    excluded = set()
    for pattern in manifest.get("exclude_globs", []):
        excluded.update(
            path.relative_to(source_root).as_posix()
            for path in source_root.glob(pattern) if path.is_file()
        )
    selected = {key: value for key, value in selected.items() if key not in excluded}
    if not selected:
        print("[FAIL] batch resolved no source files")
        return 1
    existing = {item["origin_path"]: item for item in load_sources()}
    source_set = []
    for origin, path in sorted(selected.items()):
        data = path.read_bytes()
        digest = sha_bytes(data)
        sid = source_id(origin)
        tags = tags_for(origin)
        item = existing.get(origin)
        if item:
            if item["sha256"] != digest:
                print(f"[FAIL] source changed since prior ingest: {origin}")
                return 1
            item = dict(item)
            item["snapshot_id"] = SNAPSHOT_ID
            item.pop("object_path", None)
            if item.get("source_location") == "compatibility-copy":
                item["storage_class"] = "compatibility-copy"
                item["source_location"] = "compatibility-copy"
                item["preservation"] = "verified-copy"
            else:
                try:
                    reference, copy_encoding = write_reference_copy(origin, data)
                except ValueError as exc:
                    print(f"[FAIL] {exc}")
                    return 1
                item["compatibility_paths"] = [rel(reference)]
                item["storage_class"] = "reference-copy"
                item["source_location"] = "reference-copy"
                item["copy_encoding"] = copy_encoding
                item["preservation"] = "verified-copy"
        else:
            reference, copy_encoding = write_reference_copy(origin, data)
            item = {
                "schema_version": SCHEMA_VERSION,
                "source_id": sid,
                "snapshot_id": SNAPSHOT_ID,
                "origin_path": origin,
                "origin_candidates": [origin],
                "sha256": digest,
                "bytes": len(data),
                "compatibility_paths": [rel(reference)],
                "source_kind": origin_source_kind(origin),
                "canonicality": "CANONICAL_RAW",
                "storage_class": "reference-copy",
                "source_location": "reference-copy",
                "copy_encoding": copy_encoding,
                "preservation": "verified-copy",
                "theory_tags": tags,
                "ingested_on": "2026-08-14",
                "migration_batch": manifest["batch_id"],
                "legacy_disposition": "INVENTORIED-CANDIDATE",
            }
        atomic_write_text(SOURCE_DIR / f"{sid}.json", canonical_json(item))
        source_set.append({
            "source_id": item["source_id"], "origin_path": origin,
            "sha256": digest, "bytes": len(data), "theory_tags": tags,
        })
    digest_input = "\n".join(f"{row['origin_path']}:{row['sha256']}" for row in source_set)
    resolved = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": manifest["batch_id"],
        "snapshot_id": SNAPSHOT_ID,
        "source_count": len(source_set),
        "source_set_sha256": sha_bytes(digest_input.encode("utf-8")),
        "sources": source_set,
        "warning": "hash-pinned selected reference set with repository copies; not current proof",
    }
    atomic_write_text(manifest_path.parent / "source-set.json", canonical_json(resolved))
    print(f"LEGACY-INGEST-BATCH: PASS ({manifest['batch_id']}, {len(source_set)} resolved sources)")
    return 0


def verify_selected(source_root: Path) -> int:
    errors = []
    for item in load_sources():
        path = source_root / item["origin_path"]
        if not path.is_file():
            errors.append(f"missing Contents source: {item['origin_path']}")
            continue
        if path.stat().st_size != item["bytes"]:
            errors.append(f"byte-count mismatch: {item['origin_path']}")
            continue
        if sha_file(path) != item["sha256"]:
            errors.append(f"hash mismatch: {item['origin_path']}")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print(f"LEGACY-SELECTED-VERIFY: PASS ({len(load_sources())} selected Contents references)")
    return 0


def load_sources():
    return [load_json(path) for path in sorted(SOURCE_DIR.glob("*.json"))]


def load_records():
    return [load_json(path) for path in sorted(RECORD_DIR.glob("*.json"))]


def validate_source(item, errors):
    required = {
        "schema_version", "source_id", "snapshot_id", "origin_path", "sha256",
        "bytes", "compatibility_paths", "source_kind", "canonicality",
        "storage_class", "source_location", "copy_encoding", "preservation",
    }
    missing = sorted(required - item.keys())
    if missing:
        errors.append(f"{item.get('source_id', '<unknown>')}: missing {missing}")
        return
    if item["schema_version"] != SCHEMA_VERSION:
        errors.append(f"{item['source_id']}: schema version")
    if item["source_id"] != source_id(item["origin_path"]):
        errors.append(f"{item['source_id']}: source ID/origin mismatch")
    if item["snapshot_id"] != SNAPSHOT_ID:
        errors.append(f"{item['source_id']}: snapshot mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
        errors.append(f"{item['source_id']}: invalid sha256")
    if not isinstance(item["bytes"], int) or item["bytes"] < 0:
        errors.append(f"{item['source_id']}: invalid byte count")
    if item["canonicality"] not in CANONICALITIES:
        errors.append(f"{item['source_id']}: invalid canonicality")
    if item["storage_class"] not in STORAGE_CLASSES:
        errors.append(f"{item['source_id']}: invalid storage class")
    if item["preservation"] not in AXIS_VALUES["preservation"]:
        errors.append(f"{item['source_id']}: invalid preservation state")
    if item["source_location"] not in STORAGE_CLASSES:
        errors.append(f"{item['source_id']}: invalid source location")
    if item["copy_encoding"] not in COPY_ENCODINGS:
        errors.append(f"{item['source_id']}: invalid copy encoding")
    if item["source_location"] != item["storage_class"]:
        errors.append(f"{item['source_id']}: source location/storage mismatch")
    if item["source_location"] in {"compatibility-copy", "reference-copy"} and not item["compatibility_paths"]:
        errors.append(f"{item['source_id']}: repository copy has no tracked path")
    if item["source_location"] in {"compatibility-copy", "reference-copy"} and item["copy_encoding"] == "none":
        errors.append(f"{item['source_id']}: repository copy has no encoding")
    if item["source_location"] == "contents-reference" and item["preservation"] != "inventoried":
        errors.append(f"{item['source_id']}: Contents reference must be inventoried")
    if item["source_location"] == "contents-reference" and item["copy_encoding"] != "none":
        errors.append(f"{item['source_id']}: Contents-only reference must use copy encoding none")
    for compat in item["compatibility_paths"]:
        path = REPO / compat
        if not path.is_file():
            errors.append(f"{item['source_id']}: compatibility missing/hash mismatch: {compat}")
            continue
        try:
            data = preserved_copy_bytes(item, path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if len(data) != item["bytes"] or sha_bytes(data) != item["sha256"]:
            errors.append(f"{item['source_id']}: compatibility missing/hash mismatch: {compat}")


def validate_record(item, claim_ids, source_tags, source_by_id, errors):
    required = {
        "schema_version", "record_id", "title", "source_tags", "sectors", "claims",
        "gates", "topics", "legacy_purpose", "legacy_conclusion", "achievements",
        "negative_findings", "contradictions", "assumptions", "reusable_elements",
        "current_assessment", "evidence_role", "status_axes", "tsv2_ceiling",
        "no_overclaim", "next_actions", "review", "source_ids",
        "pinned_source_ids_sha256",
    }
    missing = sorted(required - item.keys())
    if missing:
        errors.append(f"{item.get('record_id', '<unknown>')}: missing {missing}")
        return
    if item["schema_version"] != SCHEMA_VERSION:
        errors.append(f"{item['record_id']}: schema version")
    if item["current_assessment"] not in ASSESSMENTS:
        errors.append(f"{item['record_id']}: invalid assessment")
    if item["evidence_role"] not in EVIDENCE_ROLES:
        errors.append(f"{item['record_id']}: invalid evidence role")
    for sector in item["sectors"]:
        if sector not in SECTORS:
            errors.append(f"{item['record_id']}: unknown sector {sector}")
    for claim in item["claims"]:
        if claim not in claim_ids:
            errors.append(f"{item['record_id']}: unknown claim {claim}")
    for tag in item["source_tags"]:
        if tag not in source_tags:
            errors.append(f"{item['record_id']}: no source with tag {tag}")
    source_ids = item.get("source_ids", [])
    if not source_ids:
        errors.append(f"{item['record_id']}: source IDs are not pinned")
    if len(source_ids) != len(set(source_ids)):
        errors.append(f"{item['record_id']}: duplicate pinned source IDs")
    missing_sources = sorted(set(source_ids) - set(source_by_id))
    if missing_sources:
        errors.append(f"{item['record_id']}: unknown pinned sources {missing_sources}")
    expected_pin = sha_bytes("\n".join(source_ids).encode("utf-8"))
    if item.get("pinned_source_ids_sha256") != expected_pin:
        errors.append(f"{item['record_id']}: pinned source-ID digest mismatch")
    axes = item["status_axes"]
    for axis, allowed in AXIS_VALUES.items():
        if axes.get(axis) not in allowed:
            errors.append(f"{item['record_id']}: invalid {axis} axis")


def validate_batch_source_sets(source_by_id, errors):
    for batch_dir in sorted((LEGACY / "batches").glob("*")):
        if not batch_dir.is_dir():
            continue
        manifest_path = batch_dir / "manifest.json"
        source_set_path = batch_dir / "source-set.json"
        if not manifest_path.is_file() or not source_set_path.is_file():
            errors.append(f"{rel(batch_dir)}: manifest/source-set pair incomplete")
            continue
        manifest = load_json(manifest_path)
        source_set = load_json(source_set_path)
        batch_id = manifest.get("batch_id")
        if batch_id != batch_dir.name or source_set.get("batch_id") != batch_id:
            errors.append(f"{rel(batch_dir)}: batch ID mismatch")
        rows = source_set.get("sources")
        if not isinstance(rows, list):
            errors.append(f"{rel(source_set_path)}: sources is not a list")
            continue
        if source_set.get("source_count") != len(rows):
            errors.append(f"{rel(source_set_path)}: source count mismatch")
        origins = [row.get("origin_path") for row in rows]
        if len(origins) != len(set(origins)):
            errors.append(f"{rel(source_set_path)}: duplicate origin paths")
        for row in rows:
            source = source_by_id.get(row.get("source_id"))
            if source is None:
                errors.append(f"{rel(source_set_path)}: unknown source {row.get('source_id')}")
                continue
            for key in ("origin_path", "sha256", "bytes"):
                if row.get(key) != source.get(key):
                    errors.append(
                        f"{rel(source_set_path)}: {source['source_id']} {key} mismatch"
                    )
        digest_input = "\n".join(
            f"{row.get('origin_path')}:{row.get('sha256')}" for row in rows
        )
        if source_set.get("source_set_sha256") != sha_bytes(digest_input.encode("utf-8")):
            errors.append(f"{rel(source_set_path)}: source-set digest mismatch")


def validate_migration_events(errors):
    path = LEGACY / "migration" / "events.jsonl"
    if not path.is_file():
        errors.append("archive/legacy/migration/events.jsonl: missing")
        return
    event_ids = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel(path)}:{number}: invalid JSON: {exc}")
            continue
        missing = sorted({"event_id", "date", "type", "statement", "evidence", "boundary"} - event.keys())
        if missing:
            errors.append(f"{rel(path)}:{number}: missing {missing}")
        event_ids.append(event.get("event_id"))
    if len(event_ids) != len(set(event_ids)):
        errors.append(f"{rel(path)}: duplicate event IDs")


def claim_cards():
    cards = {}
    for path in sorted((REPO / "claims").glob("*/status.json")):
        item = load_json(path)
        cards[path.parent.name] = item
    return cards


def expand_records(records, sources):
    by_tag = defaultdict(list)
    for source in sources:
        for tag in source.get("theory_tags", []):
            by_tag[tag].append(source)
    expanded = []
    for record in records:
        selected = {}
        by_id = {source["source_id"]: source for source in sources}
        if record.get("source_ids"):
            for sid in record["source_ids"]:
                if sid in by_id:
                    selected[sid] = by_id[sid]
        else:
            for tag in record["source_tags"]:
                for source in by_tag[tag]:
                    selected[source["source_id"]] = source
        item = dict(record)
        item["sources"] = [selected[key] for key in sorted(selected)]
        digest_input = "\n".join(f"{s['source_id']}:{s['sha256']}" for s in item["sources"])
        item["source_set_sha256"] = sha_bytes(digest_input.encode("utf-8"))
        expanded.append(item)
    return expanded


def bullets(values):
    return [f"- {value}" for value in values] if values else ["- None recorded."]


def record_block(record):
    lines = [
        f"### {record['record_id']} -- {record['title']}",
        "",
        f"Assessment: `{record['current_assessment']}` | role: `{record['evidence_role']}` | re-validation: `{record['status_axes']['revalidation']}`",
        "",
        record["legacy_purpose"],
        "",
        "Legacy conclusion: " + record["legacy_conclusion"],
        "",
        "Sources:",
        "",
    ]
    for source in record["sources"]:
        label = f"Contents/{source['origin_path']}"
        if source["compatibility_paths"]:
            compat = ", ".join(source["compatibility_paths"])
            copy_label = "reference copy" if source["source_location"] == "reference-copy" else "compatibility copy"
            label += f" ({copy_label}: {compat})"
        lines.append(f"- `{label}`")
    lines += ["", "Achievements:", ""] + bullets(record["achievements"])
    lines += ["", "Negative or inconclusive findings:", ""] + bullets(record["negative_findings"])
    lines += ["", "Reusable elements:", ""] + bullets(record["reusable_elements"])
    lines += ["", "Boundary: " + record["no_overclaim"], ""]
    return lines


def render_research_index(expanded, sources):
    by_assessment = Counter(item["current_assessment"] for item in expanded)
    compatibility_count = sum(item["source_location"] == "compatibility-copy" for item in sources)
    reference_count = sum(item["source_location"] == "reference-copy" for item in sources)
    contents_only_count = sum(item["source_location"] == "contents-reference" for item in sources)
    lines = [
        "# Legacy research index",
        "",
        "<!-- AUTO-GENERATED by verification/scripts/legacy_research.py build -->",
        "<!-- Legacy discovery and assessment are not current proof. -->",
        "",
        f"**{len(sources)} selected source references** | **{compatibility_count} compatibility copies** | **{reference_count} preserved reference copies** | **{contents_only_count} Contents-only references** | **{len(expanded)} reviewed research records**",
        "",
        "Contents remains the maintained full corpus. Important selected sources are copied into this repository so the main line remains self-contained.",
        "The dated corpus census is retained only as [historical planning context](CONTENTS-REFERENCE.md), not as a migration denominator.",
        "",
    ]
    lines += ["## Assessment coverage", "", "| Assessment | Records |", "|---|---:|"]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(by_assessment.items()))
    lines += [
        "",
        "## Research records",
        "",
        "| Record | Source tags | Sectors | Claims | Assessment | Re-validation |",
        "|---|---|---|---|---|---|",
    ]
    for item in expanded:
        lines.append(
            f"| `{item['record_id']}` | {', '.join(item['source_tags'])} | "
            f"{', '.join(item['sectors']) or '--'} | {', '.join(item['claims']) or '--'} | "
            f"`{item['current_assessment']}` | `{item['status_axes']['revalidation']}` |"
        )
    lines += [
        "",
        "Generated navigation: [sector views](views/sectors/) and [claim views](views/claims/).",
        "Hybrid search: `python -X utf8 verification/scripts/legacy_search.py query --text \"...\"`.",
        "",
    ]
    return "\n".join(lines)


def render_sector(sector, records):
    lines = [
        f"# Sector {sector} legacy research -- {SECTORS[sector]}", "",
        "<!-- AUTO-GENERATED. Legacy material is not current proof. -->", "",
        f"Linked reviewed records: **{len(records)}**.", "",
    ]
    for record in records:
        lines.extend(record_block(record))
    return "\n".join(lines).rstrip() + "\n"


def render_claim(claim_id, card, records):
    title = card.get("title", claim_id)
    tier = card.get("tier", "unknown")
    lifecycle = card.get("lifecycle", "unknown")
    lines = [
        f"# {claim_id} legacy research view", "",
        "<!-- AUTO-GENERATED. Current claim cards remain authoritative. -->", "",
        f"Current claim: **{title}** | tier `{tier}` | lifecycle `{lifecycle}`.", "",
        f"Linked reviewed records: **{len(records)}**.", "",
    ]
    for record in records:
        lines.extend(record_block(record))
    if not records:
        lines += ["No normalized legacy research record is linked yet.", ""]
    lines += [
        "## No-overclaim", "",
        "This generated view is a retrieval surface. It cannot change the current claim tier, lifecycle, scope, dependencies, or open gates.", "",
    ]
    return "\n".join(lines)


def render_gate(gate, records):
    lines = [
        f"# {gate} legacy research view", "",
        "<!-- AUTO-GENERATED. Gate closure requires current proof authorities. -->", "",
        f"Actionable reviewed records: **{len(records)}**.", "",
    ]
    for record in records:
        lines.extend(record_block(record))
    return "\n".join(lines).rstrip() + "\n"


def expected_views(expanded, sources, cards):
    outputs = {
        RESEARCH_INDEX_MD: render_research_index(expanded, sources),
        MACHINE_INDEX: canonical_json({
            "schema_version": SCHEMA_VERSION,
            "generated": "2026-08-14",
            "warning": "legacy discovery and assessment are not current proof",
            "source_count": len(sources),
            "unique_source_hash_count": len({item["sha256"] for item in sources}),
            "record_count": len(expanded),
            "records": expanded,
        }),
    }
    for sector in SECTORS:
        selected = [item for item in expanded if sector in item["sectors"]]
        if selected:
            outputs[VIEW_ROOT / "sectors" / f"{sector}.md"] = render_sector(sector, selected)
    for claim_id, card in cards.items():
        selected = [item for item in expanded if claim_id in item["claims"]]
        if selected:
            outputs[VIEW_ROOT / "claims" / f"{claim_id}.md"] = render_claim(claim_id, card, selected)
    gates = sorted({gate for item in expanded for gate in item["gates"]})
    for gate in gates:
        selected = [item for item in expanded if gate in item["gates"]]
        outputs[VIEW_ROOT / "gates" / f"{gate}.md"] = render_gate(gate, selected)
    return outputs


def build(check: bool) -> int:
    sources = load_sources()
    records = load_records()
    cards = claim_cards()
    errors = []
    ids = [item.get("source_id") for item in sources]
    origins = [item.get("origin_path") for item in sources]
    if len(ids) != len(set(ids)):
        errors.append("duplicate source IDs")
    if len(origins) != len(set(origins)):
        errors.append("duplicate origin paths")
    for item in sources:
        validate_source(item, errors)
    source_by_id = {item["source_id"]: item for item in sources}
    source_tags = {tag for item in sources for tag in item.get("theory_tags", [])}
    record_ids = [item.get("record_id") for item in records]
    if len(record_ids) != len(set(record_ids)):
        errors.append("duplicate research record IDs")
    for item in records:
        validate_record(item, set(cards), source_tags, source_by_id, errors)
    validate_batch_source_sets(source_by_id, errors)
    validate_migration_events(errors)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    expanded = expand_records(records, sources)
    outputs = expected_views(expanded, sources, cards)
    generated_view_paths = set(VIEW_ROOT.glob("*/*.md"))
    expected_view_paths = {path for path in outputs if VIEW_ROOT in path.parents}
    extra_views = sorted(generated_view_paths - expected_view_paths)
    if check:
        stale = []
        for path, expected in outputs.items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                stale.append(rel(path))
        if stale:
            for path in stale:
                print(f"[FAIL] stale/missing generated view: {path}")
            return 1
        if extra_views:
            for path in extra_views:
                print(f"[FAIL] obsolete generated view: {rel(path)}")
            return 1
        print(f"LEGACY-RESEARCH-CHECK: PASS ({len(sources)} sources, {len(records)} records, {len(outputs)} views)")
        return 0
    for path, expected in outputs.items():
        atomic_write_text(path, expected)
    for path in extra_views:
        path.unlink()
    print(f"LEGACY-RESEARCH-BUILD: PASS ({len(sources)} sources, {len(records)} records, {len(outputs)} views)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    backfill = sub.add_parser("backfill-existing")
    backfill.add_argument("--source-root", type=Path, required=True)
    ingest = sub.add_parser("ingest-batch")
    ingest.add_argument("--source-root", type=Path, required=True)
    ingest.add_argument("--manifest", type=Path, required=True)
    verify = sub.add_parser("verify-selected")
    verify.add_argument("--source-root", type=Path, required=True)
    sub.add_parser("pin-records")
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.command == "backfill-existing":
        return backfill_existing(args.source_root.resolve())
    if args.command == "ingest-batch":
        return ingest_batch(args.source_root.resolve(), args.manifest.resolve())
    if args.command == "verify-selected":
        return verify_selected(args.source_root.resolve())
    if args.command == "pin-records":
        return pin_records()
    return build(args.check)


if __name__ == "__main__":
    sys.exit(main())
