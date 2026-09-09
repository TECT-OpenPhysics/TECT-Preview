#!/usr/bin/env python3
"""Replay a fixed PAH-OMC-020 owner-packet search snapshot.

The earlier owner inventory rescanned a changing proof worktree.  This
successor freezes the candidate-file manifest and each byte hash.  ``--check``
therefore replays the same snapshot even when later proof files are added;
``--detect-new`` is an explicit fresh scan that asks whether the snapshot must
be reopened.  This is provenance evidence only and never constructs U_n or a
temporal process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot/primary.json"
)
CANDIDATE_ROOT = ROOT / "strategy/pa-hyp"
CANDIDATE_SUFFIXES = {".json", ".md"}
MARKER_TOKENS = ("pah-omc-020", "source-authorized", "owner_authorized", "owner packet")
COMPLETE_STATUSES = {"SOURCE_AUTHORIZED_COMPLETE", "OWNER_AUTHORIZED_COMPLETE"}

PARENT_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json": "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json": "b87a2d8d7b0009c9f5bd30695823cb442376939ff18c1d48f1d890ae430fe8c7",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json": "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json": "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
    "strategy/pa-hyp/PAH-OMC-020-owner-inventory-stable-result-v1.json": "cfe872fac4517f468061cd5d644cf931e6a7e7294d66ca6a8b2faa6977d37325",
    "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json": "89e5239a6817c7046de55d4d9ba934a284ada7b1a7850035bbf63b8f14909c77",
}


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def marker_flags(path: Path, raw: bytes) -> tuple[bool, bool, bool]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, False, False
    lowered = text.lower()
    has_token = any(token in lowered for token in MARKER_TOKENS)
    authorised = False
    complete = False
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict):
            provenance = value.get("provenance")
            authorised = isinstance(provenance, dict) and provenance.get("source_authorized_packet_present") is True
            status = value.get("status")
            complete = isinstance(status, str) and status in COMPLETE_STATUSES
    return has_token, authorised, complete


def iter_candidates() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(CANDIDATE_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in CANDIDATE_SUFFIXES:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        has_token, _, _ = marker_flags(path, raw)
        if has_token:
            paths.append(path)
    return paths


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_snapshot(created_at: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    token_paths: list[str] = []
    authorised_paths: list[str] = []
    complete_paths: list[str] = []
    for path in iter_candidates():
        relative = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        has_token, authorised, complete = marker_flags(path, raw)
        if has_token:
            token_paths.append(relative)
        if authorised:
            authorised_paths.append(relative)
        if complete:
            complete_paths.append(relative)
        records.append(
            {
                "path": relative,
                "sha256": digest_bytes(raw),
                "size": len(raw),
                "authorized_marker": authorised,
                "complete_marker": complete,
            }
        )
    records.sort(key=lambda item: item["path"])
    return {
        "schema": "tect/pah-omc020-owner-search-snapshot/1.0",
        "snapshot_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-001",
        "created_at": created_at,
        "status": "FIXED_SEARCH_SNAPSHOT",
        "scope": {
            "root": "strategy/pa-hyp",
            "suffixes": [".json", ".md"],
            "selection": "Files whose UTF-8 text contains a PAH-OMC-020 or owner-authorization marker at snapshot time.",
            "replay": "--check validates only this frozen manifest; --detect-new is required before admitting a later candidate.",
        },
        "parent_hashes": PARENT_PINS,
        "candidate_records": records,
        "candidate_path_count": len(records),
        "token_paths": sorted(token_paths),
        "authorized_paths": sorted(authorised_paths),
        "complete_paths": sorted(complete_paths),
        "source_authorized_packet_present": False,
        "manifest_sha256": digest_bytes(canonical(records)),
        "reopen_condition": "A new owner candidate, any parent-hash change, or any candidate-byte change requires a new versioned snapshot.",
        "non_claims": [
            "Snapshot-time repository absence is not a universal impossibility theorem.",
            "No U_n/common-Hilbert map, N2b liminf/recovery, N2c/N4 boundary escape, N2d minimal identification or semigroup convergence.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }


def load_snapshot(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("snapshot schema", snapshot.get("schema"), "tect/pah-omc020-owner-search-snapshot/1.0", snapshot.get("schema") == "tect/pah-omc020-owner-search-snapshot/1.0")
    check("snapshot status", snapshot.get("status"), "FIXED_SEARCH_SNAPSHOT", snapshot.get("status") == "FIXED_SEARCH_SNAPSHOT")
    check("snapshot source authorization false", snapshot.get("source_authorized_packet_present"), False, snapshot.get("source_authorized_packet_present") is False)
    check("parent pin set", snapshot.get("parent_hashes"), PARENT_PINS, snapshot.get("parent_hashes") == PARENT_PINS)
    records = snapshot.get("candidate_records")
    check("candidate records are a list", isinstance(records, list), type(records).__name__, isinstance(records, list))
    paths = [record.get("path") for record in records]
    check("candidate paths sorted and unique", paths, sorted(set(paths)), paths == sorted(set(paths)))
    check("candidate count", snapshot.get("candidate_path_count"), len(records), snapshot.get("candidate_path_count") == len(records))
    check("manifest digest", snapshot.get("manifest_sha256"), digest_bytes(canonical(records)), snapshot.get("manifest_sha256") == digest_bytes(canonical(records)))

    actual_parents: dict[str, str] = {}
    for relative, expected_hash in PARENT_PINS.items():
        path = ROOT / relative
        check(f"parent present: {relative}", path.is_file(), relative, path.is_file())
        actual = digest(path)
        actual_parents[relative] = actual
        check(f"parent hash: {relative}", actual, expected_hash, actual == expected_hash)

    authorised: list[str] = []
    complete: list[str] = []
    for record in records:
        relative = record["path"]
        path = ROOT / relative
        check(f"candidate present: {relative}", path.is_file(), relative, path.is_file())
        raw = path.read_bytes()
        actual_hash = digest_bytes(raw)
        check(f"candidate hash: {relative}", actual_hash, record["sha256"], actual_hash == record["sha256"])
        has_token, is_authorised, is_complete = marker_flags(path, raw)
        check(f"candidate marker retained: {relative}", has_token, True, has_token)
        check(f"candidate authorization flag: {relative}", is_authorised, record["authorized_marker"], is_authorised == record["authorized_marker"])
        check(f"candidate completion flag: {relative}", is_complete, record["complete_marker"], is_complete == record["complete_marker"])
        if is_authorised:
            authorised.append(relative)
        if is_complete:
            complete.append(relative)
    check("no authorized candidate", sorted(authorised), [], not authorised and snapshot.get("authorized_paths") == [])
    check("no complete candidate", sorted(complete), [], not complete and snapshot.get("complete_paths") == [])
    check("parent output is not dynamic fsck", "fsck" in json.dumps(snapshot).lower(), False, "fsck" not in json.dumps(snapshot).lower())

    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-check/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-CHECK-001",
        "status": "PASS_FIXED_OWNER_SNAPSHOT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "source_hashes": actual_parents,
        "snapshot_id": snapshot.get("snapshot_id"),
        "candidate_path_count": len(records),
        "authorized_paths": sorted(authorised),
        "complete_paths": sorted(complete),
        "manifest_sha256": snapshot.get("manifest_sha256"),
        "finding": "The fixed candidate manifest and all pinned parent bytes replay exactly, and no snapshot candidate declares source authorization or completion. This is snapshot-time provenance evidence only.",
        "next_single_question": "Can a source owner supply a versioned packet with all N2a--N2d fields, or does --detect-new identify a later candidate requiring a new snapshot?",
        "non_claims": snapshot.get("non_claims", []),
    }


def detect_new(snapshot: dict[str, Any]) -> dict[str, Any]:
    frozen = {record["path"]: record["sha256"] for record in snapshot.get("candidate_records", [])}
    current = {path.relative_to(ROOT).as_posix(): digest(path) for path in iter_candidates()}
    added = sorted(set(current) - set(frozen))
    removed = sorted(set(frozen) - set(current))
    changed = sorted(path for path in set(current) & set(frozen) if current[path] != frozen[path])
    return {"added": added, "removed": removed, "changed": changed, "fresh": not added and not removed and not changed}


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        temporary.write_bytes(payload)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true", help="create the fixed snapshot")
    parser.add_argument("--created-at", default="2026-09-07T20:00:00Z")
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--detect-new", action="store_true")
    args = parser.parse_args()
    snapshot_path = args.snapshot.resolve()
    if args.create:
        snapshot = build_snapshot(args.created_at)
        atomic_write(snapshot_path, (json.dumps(snapshot, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
        print(f"PAH-OMC-020 OWNER SNAPSHOT: created {snapshot_path} ({snapshot['candidate_path_count']} candidates)")
        return 0
    snapshot = load_snapshot(snapshot_path)
    if args.detect_new:
        fresh = detect_new(snapshot)
        print(json.dumps(fresh, indent=2, sort_keys=True))
        return 0 if fresh["fresh"] else 2
    payload = validate_snapshot(snapshot)
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("fixed owner snapshot replay mismatch")
    else:
        atomic_write(args.output.resolve(), encoded)
    print(f"PAH-OMC-020 OWNER SNAPSHOT: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
