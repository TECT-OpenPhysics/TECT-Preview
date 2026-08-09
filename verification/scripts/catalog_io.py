#!/usr/bin/env python3
"""Validated reader for the current sharded derived catalog.

New code imports this module instead of reading the frozen full-JSON
compatibility volume.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-08-10"
__version_issued__ = "2026-08-10"

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = Path("verification/catalog/index.json")


def _inside(repo: Path, relative: str) -> Path:
    path = (repo / relative).resolve()
    root = repo.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"catalog shard escapes repository: {relative}") from exc
    return path


def load_entries(repo: Path = REPO, kind: str | None = None) -> list[dict]:
    repo = Path(repo)
    manifest_path = _inside(repo, MANIFEST.as_posix())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "tect/catalog-manifest/2.0":
        raise ValueError("unsupported catalog manifest schema")
    descriptors = manifest.get("shards", [])
    if kind is not None:
        descriptors = [row for row in descriptors if row.get("kind") == kind]
        if not descriptors:
            raise KeyError(f"unknown catalog kind: {kind}")
    entries = []
    for descriptor in descriptors:
        path = _inside(repo, str(descriptor["path"]))
        data = path.read_bytes()
        if len(data) != descriptor["bytes"]:
            raise ValueError(f"catalog shard size mismatch: {descriptor['path']}")
        if hashlib.sha256(data).hexdigest() != descriptor["sha256"]:
            raise ValueError(f"catalog shard hash mismatch: {descriptor['path']}")
        payload = json.loads(data.decode("utf-8"))
        if payload.get("schema") != "tect/catalog-kind/1.0":
            raise ValueError(f"unsupported shard schema: {descriptor['path']}")
        if payload.get("kind") != descriptor["kind"]:
            raise ValueError(f"catalog shard kind mismatch: {descriptor['path']}")
        rows = payload.get("entries", [])
        if len(rows) != descriptor["count"] or payload.get("count") != len(rows):
            raise ValueError(f"catalog shard count mismatch: {descriptor['path']}")
        entries.extend(rows)
    if kind is None and len(entries) != manifest.get("total"):
        raise ValueError("catalog manifest total mismatch")
    paths = [row.get("path") for row in entries]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate catalog path")
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind")
    parser.add_argument("--path")
    parser.add_argument("--claim")
    args = parser.parse_args()
    rows = load_entries(kind=args.kind)
    if args.path:
        needle = args.path.casefold()
        rows = [row for row in rows if needle in row["path"].casefold()]
    if args.claim:
        rows = [row for row in rows if args.claim in row.get("claims", [])]
    for row in rows:
        print(f"{row['kind']:<18} {row['path']}")
    print(f"{len(rows)} match(es).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
