"""Deterministic sharding and reconstruction for the proof-evidence map.

The logical map remains the same complete projection produced by
``build_proof_evidence_map.py``.  The on-disk representation is an index plus
small, hash-pinned shards so consumers do not need to load a multi-megabyte
single JSON object.  This module contains no authority logic: it only checks
serialization, hashes, coverage, and lossless round-tripping.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


INDEX_SCHEMA = "tect/proof-evidence-map-index/1.0"
SHARD_SCHEMA = "tect/proof-evidence-map-shard/1.0"
SHARD_DIR_NAME = "verification/proof-evidence-map"
INDEX_NAME = "verification/proof-evidence-map.json"
CHUNK_SIZE = 100

LIST_KINDS = (
    "claims",
    "reusable_results",
    "negative_records",
    "proof_explorations",
    "accepted_events",
    "all_tasks",
)
GRAPH_KINDS = ("graph_nodes", "graph_edges")


def canonical_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def digest_text(value: str) -> str:
    return digest_bytes(value.encode("utf-8"))


def _parts(values: list[Any]) -> list[list[Any]]:
    return [values[start : start + CHUNK_SIZE] for start in range(0, len(values), CHUNK_SIZE)] or [[]]


def build_index_and_shards(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Return the compact index and canonical shard texts for ``data``."""

    shard_values: list[tuple[str, int, Any, int]] = []
    for kind in LIST_KINDS:
        values = list(data[kind])
        for part, chunk in enumerate(_parts(values), start=1):
            shard_values.append((kind, part, chunk, len(chunk)))
    graph = data["graph"]
    for kind, values in (("graph_nodes", list(graph["nodes"])), ("graph_edges", list(graph["edges"]))):
        for part, chunk in enumerate(_parts(values), start=1):
            shard_values.append((kind, part, chunk, len(chunk)))

    core = {key: value for key, value in data.items() if key not in LIST_KINDS and key != "graph"}
    core["graph_metadata"] = {
        key: value for key, value in graph.items() if key not in {"nodes", "edges"}
    }
    shard_values.insert(0, ("core", 1, core, len(core)))

    shards: dict[str, str] = {}
    entries: list[dict[str, Any]] = []
    for kind, part, payload, record_count in shard_values:
        filename = f"{kind}-{part:04d}.json"
        relative = f"{SHARD_DIR_NAME}/{filename}"
        body = {"schema": SHARD_SCHEMA, "map_schema": data["schema"], "kind": kind, "part": part, "data": payload}
        text = canonical_text(body)
        shards[relative] = text
        encoded = text.encode("utf-8")
        entries.append(
            {
                "path": relative,
                "kind": kind,
                "part": part,
                "record_count": record_count,
                "bytes": len(encoded),
                "sha256": digest_bytes(encoded),
            }
        )

    logical_hash = digest_bytes(canonical_bytes(data))
    index = {
        "schema": INDEX_SCHEMA,
        "map_schema": data["schema"],
        "generator": data["generator"],
        "logical_map_sha256": logical_hash,
        "coverage": data["coverage"],
        "shard_count": len(entries),
        "shards": entries,
        "loader": "verification/scripts/proof_evidence_map_io.py",
        "boundary": "The shards are a lossless serialization of the generated proof-evidence map; canonical authorities remain unchanged.",
    }
    return index, shards


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_map(repo: Path) -> dict[str, Any]:
    """Load and verify the complete logical map from its index and shards."""

    index_path = repo / INDEX_NAME
    index = _read_json(index_path)
    if index.get("schema") != INDEX_SCHEMA:
        raise ValueError(f"unexpected map index schema: {index.get('schema')!r}")
    assembled: dict[str, Any] = {}
    graph_nodes: list[Any] = []
    graph_edges: list[Any] = []
    for entry in sorted(
        index.get("shards", []),
        key=lambda item: (0 if item["kind"] == "core" else 1, item["kind"], item["part"]),
    ):
        path = repo / entry["path"]
        raw = path.read_bytes()
        if digest_bytes(raw) != entry["sha256"]:
            raise ValueError(f"proof-evidence shard hash mismatch: {entry['path']}")
        body = json.loads(raw.decode("utf-8"))
        if body.get("schema") != SHARD_SCHEMA or body.get("map_schema") != index.get("map_schema"):
            raise ValueError(f"invalid proof-evidence shard header: {entry['path']}")
        kind = body["kind"]
        payload = body["data"]
        if kind == "core":
            if body["part"] != 1 or assembled:
                raise ValueError("duplicate or misplaced core shard")
            assembled.update(payload)
        elif kind in LIST_KINDS:
            assembled.setdefault(kind, []).extend(payload)
        elif kind == "graph_nodes":
            graph_nodes.extend(payload)
        elif kind == "graph_edges":
            graph_edges.extend(payload)
        else:
            raise ValueError(f"unknown proof-evidence shard kind: {kind}")
    if set(LIST_KINDS) - set(assembled):
        raise ValueError("missing proof-evidence list shard")
    graph_metadata = assembled.pop("graph_metadata", {})
    assembled["graph"] = {**graph_metadata, "nodes": graph_nodes, "edges": graph_edges}
    if digest_bytes(canonical_bytes(assembled)) != index.get("logical_map_sha256"):
        raise ValueError("proof-evidence logical map round-trip hash mismatch")
    return assembled


def expected_paths(index: dict[str, Any]) -> set[str]:
    return {str(entry["path"]) for entry in index.get("shards", [])}
