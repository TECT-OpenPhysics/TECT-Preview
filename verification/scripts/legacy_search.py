#!/usr/bin/env python3
"""Offline hybrid search for normalized TECT legacy research.

The default vector backend is deterministic hashed TF-IDF. It is a vector
retrieval baseline, not a dense semantic model. Korean domain aliases provide
bounded cross-language recall until a pinned local multilingual model is
installed and recorded.
"""

__version__ = "1.1.0"
__first_issued__ = "2026-08-14"
__version_issued__ = "2026-08-14"

import argparse
import base64
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import numpy as np
except ImportError:  # release self-test remains stdlib-only
    np = None
from array import array


REPO = Path(__file__).resolve().parents[2]
LEGACY = REPO / "archive" / "legacy"
CONFIG_PATH = LEGACY / "search-config.json"
ALIASES_PATH = LEGACY / "search-aliases.json"
MACHINE_INDEX = REPO / "verification" / "legacy-research-index.json"
CACHE_DIR = LEGACY / ".search"
DB_PATH = CACHE_DIR / "legacy-search.sqlite3"
TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)
BOUNDARY_RE = re.compile(
    r"^\s*(?:#{1,6}\s|\\(?:part|chapter|section|subsection|subsubsection)\b|(?:async\s+)?def\s+|class\s+)",
    re.IGNORECASE,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text) if len(token) > 1]


def expand_query(text: str, aliases: dict) -> str:
    expanded = [text]
    folded = text.casefold()
    for phrase, values in aliases.items():
        if phrase.casefold() in folded:
            expanded.extend(values)
    return " ".join(expanded)


def decode_source(data: bytes):
    if b"\x00" in data:
        return None
    for encoding in ("utf-8", "cp949"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def chunk_lines(text: str, max_lines: int, overlap: int):
    lines = text.splitlines()
    if not lines:
        return []
    starts = [0]
    for index, line in enumerate(lines):
        if index and BOUNDARY_RE.match(line) and index - starts[-1] >= 12:
            starts.append(index)
        elif index - starts[-1] >= max_lines:
            starts.append(max(index - overlap, starts[-1] + 1))
    chunks = []
    for position, start in enumerate(starts):
        next_start = starts[position + 1] if position + 1 < len(starts) else len(lines)
        end = min(len(lines), max(next_start, start + 1))
        body = "\n".join(lines[start:end]).strip()
        if body:
            chunks.append((start + 1, end, body))
    return chunks


def corpus_digest(index: dict, config: dict, aliases: dict) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(config, sort_keys=True).encode())
    h.update(json.dumps(aliases, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for record in index["records"]:
        h.update(record["record_id"].encode())
        h.update(record["source_set_sha256"].encode())
    return h.hexdigest()


def metadata_for_sources(index: dict):
    result = defaultdict(lambda: {
        "sectors": set(), "claims": set(), "gates": set(), "records": set(),
        "assessments": set(), "roles": set(), "revalidations": set(),
    })
    sources = {}
    for record in index["records"]:
        for source in record["sources"]:
            sid = source["source_id"]
            sources[sid] = source
            meta = result[sid]
            meta["sectors"].update(record["sectors"])
            meta["claims"].update(record["claims"])
            meta["gates"].update(record["gates"])
            meta["records"].add(record["record_id"])
            meta["assessments"].add(record["current_assessment"])
            meta["roles"].add(record["evidence_role"])
            meta["revalidations"].add(record["status_axes"]["revalidation"])
    return sources, result


def hash_bucket(token: str, dimension: int):
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "big")
    return value % dimension, -1.0 if value & (1 << 63) else 1.0


def vectorize(tokens: list[str], df: dict[str, int], n_docs: int, dimension: int):
    values = [0.0] * dimension
    counts = Counter(tokens)
    for token, count in counts.items():
        index, sign = hash_bucket(token, dimension)
        idf = math.log((1.0 + n_docs) / (1.0 + df.get(token, 0))) + 1.0
        values[index] += sign * (1.0 + math.log(count)) * idf
    norm = math.sqrt(sum(value * value for value in values))
    if norm:
        values = [value / norm for value in values]
    if np is not None:
        return np.asarray(values, dtype=np.float32)
    return array("f", values)

def selected_source_root(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        return explicit.resolve()
    configured = os.environ.get("TECT_LEGACY_SOURCE_ROOT")
    if configured:
        return Path(configured).resolve()
    sibling = REPO.parent / "Contents"
    return sibling if sibling.is_dir() else None


def preserved_source_bytes(source: dict, path: Path) -> bytes:
    encoding = source.get("copy_encoding", "raw")
    if encoding == "raw" or encoding == "none":
        return path.read_bytes()
    if encoding != "base64-json":
        raise ValueError(f"unsupported selected source encoding: {encoding}")
    wrapper = load_json(path)
    if wrapper.get("origin_path") != source["origin_path"]:
        raise ValueError(f"selected legacy source wrapper origin drift: {path}")
    try:
        return base64.b64decode(wrapper["payload_base64"], validate=True)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"selected legacy source wrapper is invalid: {path}") from exc


def resolve_source(source: dict, source_root: Path | None):
    if source["compatibility_paths"]:
        locator = source["compatibility_paths"][0]
        path = REPO / locator
    else:
        if source_root is None:
            raise FileNotFoundError(
                "selected Contents sources are unavailable; pass --source-root or set TECT_LEGACY_SOURCE_ROOT"
            )
        locator = f"Contents/{source['origin_path']}"
        path = source_root / source["origin_path"]
    if not path.is_file():
        raise FileNotFoundError(f"selected legacy source missing: {locator}")
    data = preserved_source_bytes(source, path)
    if len(data) != source["bytes"]:
        raise ValueError(f"selected legacy source byte-count drift: {locator}")
    if hashlib.sha256(data).hexdigest() != source["sha256"]:
        raise ValueError(f"selected legacy source hash drift: {locator}")
    return path, locator, data


def verify_selected_sources(index: dict, source_root: Path | None):
    sources, _ = metadata_for_sources(index)
    for source in sources.values():
        resolve_source(source, source_root)


def prepare_chunks(index: dict, config: dict, source_root: Path | None):
    sources, source_meta = metadata_for_sources(index)
    chunks = []
    seen_objects = set()
    for sid, source in sorted(sources.items()):
        if source["sha256"] in seen_objects:
            continue
        seen_objects.add(source["sha256"])
        _path, locator, data = resolve_source(source, source_root)
        text = decode_source(data)
        if text is None:
            continue
        meta = source_meta[sid]
        for ordinal, (line_start, line_end, body) in enumerate(
            chunk_lines(text, config["max_lines"], config["overlap_lines"]), 1
        ):
            chunk_id = f"{sid}-C{ordinal:04d}"
            chunks.append({
                "chunk_id": chunk_id,
                "source_id": sid,
                "origin_path": source["origin_path"],
                "source_locator": locator,
                "sha256": source["sha256"],
                "line_start": line_start,
                "line_end": line_end,
                "text": body,
                "sectors": sorted(meta["sectors"]),
                "claims": sorted(meta["claims"]),
                "gates": sorted(meta["gates"]),
                "records": sorted(meta["records"]),
                "assessments": sorted(meta["assessments"]),
                "roles": sorted(meta["roles"]),
                "revalidations": sorted(meta["revalidations"]),
            })
    return chunks


def build(db_path: Path = DB_PATH, source_root: Path | None = None):
    config = load_json(CONFIG_PATH)
    aliases = load_json(ALIASES_PATH)
    index = load_json(MACHINE_INDEX)
    digest = corpus_digest(index, config, aliases)
    source_root = selected_source_root(source_root)
    chunks = prepare_chunks(index, config, source_root)
    token_lists = [tokenize(chunk["text"]) for chunk in chunks]
    df = Counter()
    for tokens in token_lists:
        df.update(set(tokens))
    vectors = [
        vectorize(tokens, df, len(chunks), config["vector_dimension"])
        for tokens in token_lists
    ]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript("""
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY, source_id TEXT NOT NULL,
                origin_path TEXT NOT NULL, source_locator TEXT NOT NULL,
                sha256 TEXT NOT NULL, line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL, text TEXT NOT NULL,
                sectors TEXT NOT NULL, claims TEXT NOT NULL, gates TEXT NOT NULL,
                records TEXT NOT NULL, assessments TEXT NOT NULL,
                roles TEXT NOT NULL, revalidations TEXT NOT NULL,
                vector BLOB NOT NULL
            );
            CREATE VIRTUAL TABLE fts USING fts5(chunk_id UNINDEXED, text, tokenize='unicode61');
            CREATE TABLE document_frequency (token TEXT PRIMARY KEY, count INTEGER NOT NULL);
        """)
        metadata = {
            "corpus_digest": digest,
            "config": json.dumps(config, sort_keys=True),
            "chunk_count": str(len(chunks)),
            "dense_semantic_status": config["dense_semantic_backend"]["status"],
            "warning": config["warning"],
        }
        con.executemany("INSERT INTO metadata VALUES (?,?)", metadata.items())
        con.executemany(
            "INSERT INTO document_frequency VALUES (?,?)",
            sorted(df.items()),
        )
        for chunk, vector in zip(chunks, vectors):
            values = (
                chunk["chunk_id"], chunk["source_id"], chunk["origin_path"],
                chunk["source_locator"], chunk["sha256"], chunk["line_start"],
                chunk["line_end"], chunk["text"], json.dumps(chunk["sectors"]),
                json.dumps(chunk["claims"]), json.dumps(chunk["gates"]),
                json.dumps(chunk["records"]), json.dumps(chunk["assessments"]),
                json.dumps(chunk["roles"]), json.dumps(chunk["revalidations"]),
                vector.tobytes(),
            )
            con.execute("INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
            con.execute("INSERT INTO fts VALUES (?,?)", (chunk["chunk_id"], chunk["text"]))
        con.commit()
    finally:
        con.close()
    print(f"LEGACY-SEARCH-BUILD: PASS ({len(chunks)} chunks, hashed-tfidf-v1, dense semantic UNCONFIGURED)")


def current_digest():
    return corpus_digest(load_json(MACHINE_INDEX), load_json(CONFIG_PATH), load_json(ALIASES_PATH))


def ensure_index(source_root: Path | None = None):
    source_root = selected_source_root(source_root)
    index = load_json(MACHINE_INDEX)
    verify_selected_sources(index, source_root)
    if not DB_PATH.exists():
        build(source_root=source_root)
        return
    con = sqlite3.connect(DB_PATH)
    try:
        row = con.execute("SELECT value FROM metadata WHERE key='corpus_digest'").fetchone()
    finally:
        con.close()
    if row is None or row[0] != current_digest():
        build(source_root=source_root)


def matches(row, args):
    checks = [
        (args.sector, "sectors"), (args.claim, "claims"), (args.gate, "gates"),
        (args.assessment, "assessments"), (args.role, "roles"),
    ]
    for value, field in checks:
        if value and value not in json.loads(row[field]):
            return False
    return True


def vector_dot(left, right):
    return sum(float(a) * float(b) for a, b in zip(left, right))


def vector_blob_dot(vector, blob):
    if np is not None:
        return float(np.dot(vector, np.frombuffer(blob, dtype=np.float32)))
    values = struct.unpack(f"{len(vector)}f", blob)
    return vector_dot(vector, values)


def query(args):
    ensure_index(args.source_root)
    config = load_json(CONFIG_PATH)
    aliases = load_json(ALIASES_PATH)
    expanded = expand_query(args.text, aliases)
    tokens = tokenize(expanded)
    if not tokens:
        raise ValueError("query has no searchable tokens")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        df = dict(con.execute("SELECT token,count FROM document_frequency"))
        n_docs = int(con.execute("SELECT value FROM metadata WHERE key='chunk_count'").fetchone()[0])
        rows = list(con.execute("SELECT * FROM chunks"))
        eligible = [row for row in rows if matches(row, args)]
        qvec = vectorize(tokens, df, n_docs, config["vector_dimension"])
        vector_ranked = sorted(
            eligible,
            key=lambda row: vector_blob_dot(qvec, row["vector"]),
            reverse=True,
        )
        fts_tokens = sorted(set(tokens))
        fts_expr = " OR ".join('"' + token.replace('"', '""') + '"' for token in fts_tokens)
        lexical_ids = []
        try:
            lexical_ids = [row[0] for row in con.execute(
                "SELECT chunk_id FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT 500",
                (fts_expr,),
            )]
        except sqlite3.OperationalError:
            lexical_ids = []
        eligible_ids = {row["chunk_id"] for row in eligible}
        lexical_ids = [cid for cid in lexical_ids if cid in eligible_ids]
        scores = defaultdict(float)
        k = config["rrf_k"]
        for rank, cid in enumerate(lexical_ids, 1):
            scores[cid] += 1.0 / (k + rank)
        for rank, row in enumerate(vector_ranked[:500], 1):
            scores[row["chunk_id"]] += 1.0 / (k + rank)
        by_id = {row["chunk_id"]: row for row in eligible}
        ranked = sorted(scores, key=lambda cid: (-scores[cid], cid))[: args.limit]
        result = []
        for cid in ranked:
            row = by_id[cid]
            result.append({
                "rrf_score": scores[cid], "chunk_id": cid,
                "source_id": row["source_id"], "origin_path": row["origin_path"],
                "source_locator": row["source_locator"], "sha256": row["sha256"],
                "line_start": row["line_start"], "line_end": row["line_end"],
                "sectors": json.loads(row["sectors"]), "claims": json.loads(row["claims"]),
                "gates": json.loads(row["gates"]), "assessments": json.loads(row["assessments"]),
                "roles": json.loads(row["roles"]), "revalidations": json.loads(row["revalidations"]),
                "preview": row["text"][:400].replace("\n", " "),
                "warning": config["warning"],
            })
    finally:
        con.close()
    if args.json:
        print(json.dumps({"query": args.text, "expanded": expanded, "results": result}, ensure_ascii=False, indent=2))
    else:
        print(f"Query: {args.text}")
        if expanded != args.text:
            print(f"Expanded: {expanded}")
        print("Backend: FTS5 + hashed-tfidf-v1 + RRF; dense semantic UNCONFIGURED")
        print("Warning: legacy discovery result; not current proof")
        for number, item in enumerate(result, 1):
            print(f"\n{number}. {item['origin_path']}:{item['line_start']}-{item['line_end']}")
            print(f"   source={item['source_id']} sha256={item['sha256'][:16]} claims={','.join(item['claims']) or '--'} assessment={','.join(item['assessments'])}")
            print(f"   {item['preview']}")
    return 0


def selftest():
    aliases = {"\uc808\ub2e8\ud314\uba74\uccb4": ["truncated octahedron"]}
    assert "truncated octahedron" in expand_query(
        "\uc808\ub2e8\ud314\uba74\uccb4 \uad6c\uc870", aliases
    )
    chunks = chunk_lines("# A\nalpha beta\n# B\ngamma delta", 80, 10)
    assert chunks and chunks[0][0] == 1
    df = {"alpha": 1, "beta": 1, "gamma": 1}
    a = vectorize(["alpha", "beta"], df, 2, 64)
    b = vectorize(["alpha"], df, 2, 64)
    c = vectorize(["gamma"], df, 2, 64)
    assert vector_dot(a, b) > vector_dot(a, c)
    print("LEGACY-SEARCH-SELFTEST: PASS (chunking, Korean alias, vector ordering)")
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--source-root", type=Path)
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--source-root", type=Path)
    sub.add_parser("selftest")
    q = sub.add_parser("query")
    q.add_argument("--text", required=True)
    q.add_argument("--sector")
    q.add_argument("--claim")
    q.add_argument("--gate")
    q.add_argument("--assessment")
    q.add_argument("--role")
    q.add_argument("--limit", type=int, default=10)
    q.add_argument("--json", action="store_true")
    q.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(source_root=args.source_root)
        return 0
    if args.command == "status":
        ensure_index(args.source_root)
        con = sqlite3.connect(DB_PATH)
        try:
            meta = dict(con.execute("SELECT key,value FROM metadata"))
        finally:
            con.close()
        print(json.dumps(meta, indent=2, sort_keys=True))
        return 0
    if args.command == "selftest":
        return selftest()
    return query(args)


if __name__ == "__main__":
    sys.exit(main())
