#!/usr/bin/env python3
"""Bounded current-byte delta check for the canonical owner source root."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENTS = Path("E:/Dev/Contents")
DEFAULT_CUTOFF = "2026-09-08T13:50:00Z"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-delta-after-r566/delta.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return encoded


def parse_cutoff(value: str) -> dt.datetime:
    parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return parsed.replace(tzinfo=dt.timezone.utc)


def snapshot(contents_root: Path, cutoff: dt.datetime) -> dict[str, Any]:
    if not contents_root.is_dir():
        return {
            "schema": "tect/pah-omc020-owner-delta/1.0",
            "status": "UNAVAILABLE",
            "source_root": str(contents_root),
            "cutoff_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reason": "canonical Contents root is not available",
        }
    files = [path for path in contents_root.rglob("*") if path.is_file()]
    fresh = [path for path in files if path.stat().st_mtime_ns > cutoff.timestamp() * 1_000_000_000 or path.stat().st_ctime_ns > cutoff.timestamp() * 1_000_000_000]
    latest = max(files, key=lambda path: path.stat().st_mtime_ns) if files else None
    payload = {
        "schema": "tect/pah-omc020-owner-delta/1.0",
        "status": "PASS_NO_NEW_INPUT" if not fresh else "NEW_INPUT_PRESENT",
        "source_root": str(contents_root),
        "cutoff_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_files": len(files),
        "fresh_after_cutoff": len(fresh),
        "fresh_paths": sorted(str(path) for path in fresh)[:20],
        "latest_path": str(latest) if latest else None,
        "latest_mtime_utc": dt.datetime.fromtimestamp(latest.stat().st_mtime, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if latest else None,
        "scope": "Bounded filesystem delta only; no semantic owner admission or universal absence claim.",
        "next_action": "Wait for one versioned source-authorized packet; do not repeat the full owner search while the delta remains empty.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contents-root", type=Path, default=DEFAULT_CONTENTS)
    parser.add_argument("--cutoff", default=DEFAULT_CUTOFF)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = snapshot(args.contents_root, parse_cutoff(args.cutoff))
    if payload["status"] == "UNAVAILABLE":
        raise SystemExit(payload["reason"])
    if payload["status"] == "NEW_INPUT_PRESENT":
        raise SystemExit("new canonical source input detected; do not classify as a hold")
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 owner delta replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 OWNER DELTA: PASS total={payload['total_files']}; fresh_after_cutoff=0; status=PASS_NO_NEW_INPUT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
