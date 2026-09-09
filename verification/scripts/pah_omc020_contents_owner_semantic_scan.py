#!/usr/bin/env python3
"""Bounded semantic scan for an external PAH-OMC-020 owner packet.

This scan is an admission aid, not a universal absence theorem.  A candidate
must be a parsed JSON object with explicit source authorization and all
required owner-packet fields.  Prose mentions and labels are reported only as
keyword hits and cannot create admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENTS = Path(r"E:\Dev\Contents")
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-semantic-scan/scan.json"
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
KEYWORD_PATTERNS = {
    "source_authorized_packet_present": re.compile(r"source_authorized_packet_present", re.I),
    "owner_payload": re.compile(r"owner_payload", re.I),
    "common_hilbert_realization": re.compile(r"common_hilbert_realization", re.I),
    "n2b_liminf": re.compile(r"n2b_liminf", re.I),
    "n2d_minimal_identification": re.compile(r"n2d_minimal_identification", re.I),
    "anchored_D": re.compile(r"anchored_D", re.I),
    "full_domain_J": re.compile(r"full_domain_J", re.I),
}
REQUIRED_FIELDS = (
    "owner_authority",
    "common_hilbert_realization",
    "n2b_liminf",
    "recovery_limsup",
    "n2c_n4_boundary_escape",
    "n2d_minimal_identification",
    "verification",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def nested_sections(payload: dict[str, Any]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = [payload]
    for key in ("provenance", "owner_payload", "snapshot", "current_status"):
        value = payload.get(key)
        if isinstance(value, dict):
            sections.append(value)
    return sections


def strict_candidate(payload: dict[str, Any]) -> bool:
    sections = nested_sections(payload)
    authorized = any(
        section.get("source_authorized_packet_present") is True or section.get("source_authorized") is True
        for section in sections
    )
    if not authorized:
        return False
    owner_payload = payload.get("owner_payload")
    if not isinstance(owner_payload, dict):
        return False
    return all(
        isinstance(owner_payload.get(field), dict)
        and any(owner_payload[field].get(marker) for marker in ("evidence", "statement", "path"))
        for field in REQUIRED_FIELDS
    )


def scan(contents: Path) -> dict[str, Any]:
    if not contents.is_dir():
        return {
            "schema": "tect/pah-omc020-owner-semantic-scan/1.0",
            "status": "UNAVAILABLE",
            "source_root": str(contents),
            "reason": "canonical Contents root is not available",
        }
    files = sorted(path for path in contents.rglob("*") if path.is_file())
    text_files = [path for path in files if path.suffix.lower() in TEXT_SUFFIXES]
    keyword_hits: dict[str, int] = {key: 0 for key in KEYWORD_PATTERNS}
    keyword_paths: dict[str, list[str]] = {key: [] for key in KEYWORD_PATTERNS}
    candidates: list[str] = []
    malformed_json = 0
    for path in text_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        relative = path.relative_to(contents).as_posix()
        for key, pattern in KEYWORD_PATTERNS.items():
            if pattern.search(text):
                keyword_hits[key] += 1
                if len(keyword_paths[key]) < 20:
                    keyword_paths[key].append(relative)
        if path.suffix.lower() != ".json":
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            malformed_json += 1
            continue
        if isinstance(payload, dict) and strict_candidate(payload):
            candidates.append(relative)
    return {
        "schema": "tect/pah-omc020-owner-semantic-scan/1.0",
        "status": "PASS_NO_STRICT_OWNER_CANDIDATE" if not candidates else "OWNER_CANDIDATE_PRESENT",
        "source_root": str(contents),
        "total_files": len(files),
        "text_files": len(text_files),
        "malformed_json": malformed_json,
        "keyword_hits": keyword_hits,
        "keyword_paths_sample": keyword_paths,
        "strict_owner_candidates": candidates,
        "required_fields": list(REQUIRED_FIELDS),
        "scope": "Bounded semantic scan of the current Contents tree; no universal absence claim and no source authorization inferred from prose.",
        "next_action": "Admit only a versioned source-authorized packet with all required fields; otherwise keep the PAH-OMC-020 successor route on hold.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contents-root", type=Path, default=DEFAULT_CONTENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = scan(args.contents_root)
    if payload["status"] == "UNAVAILABLE":
        raise SystemExit(payload["reason"])
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 semantic owner scan replay mismatch")
    else:
        atomic_json(destination, payload)
    print(
        f"PAH-OMC-020 OWNER SEMANTIC SCAN: {payload['status']} "
        f"files={payload['total_files']} text={payload['text_files']} "
        f"strict_candidates={len(payload['strict_owner_candidates'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
