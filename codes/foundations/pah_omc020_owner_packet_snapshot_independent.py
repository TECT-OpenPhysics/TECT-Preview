#!/usr/bin/env python3
"""Independent replay of the frozen PAH-OMC-020 owner search snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot/independent.json"
)
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json": "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json": "b87a2d8d7b0009c9f5bd30695823cb442376939ff18c1d48f1d890ae430fe8c7",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json": "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json": "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
    "strategy/pa-hyp/PAH-OMC-020-owner-inventory-stable-result-v1.json": "cfe872fac4517f468061cd5d644cf931e6a7e7294d66ca6a8b2faa6977d37325",
    "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json": "89e5239a6817c7046de55d4d9ba934a284ada7b1a7850035bbf63b8f14909c77",
}
MARKERS = ("pah-omc-020", "source-authorized", "owner_authorized", "owner packet")
COMPLETE = {"SOURCE_AUTHORIZED_COMPLETE", "OWNER_AUTHORIZED_COMPLETE"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def flags(path: Path, raw: bytes) -> tuple[bool, bool, bool]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, False, False
    token = any(item in text.lower() for item in MARKERS)
    authorised = False
    complete = False
    if path.suffix.lower() == ".json":
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict):
            provenance = obj.get("provenance")
            authorised = isinstance(provenance, dict) and provenance.get("source_authorized_packet_present") is True
            status = obj.get("status")
            complete = isinstance(status, str) and status in COMPLETE
    return token, authorised, complete


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def compute() -> dict[str, Any]:
    snapshot = load(SNAPSHOT)
    records = snapshot.get("candidate_records", [])
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(name)

    check("snapshot schema", snapshot.get("schema"), "tect/pah-omc020-owner-search-snapshot/1.0", snapshot.get("schema") == "tect/pah-omc020-owner-search-snapshot/1.0")
    check("snapshot is fixed", snapshot.get("status"), "FIXED_SEARCH_SNAPSHOT", snapshot.get("status") == "FIXED_SEARCH_SNAPSHOT")
    check("snapshot authorization false", snapshot.get("source_authorized_packet_present"), False, snapshot.get("source_authorized_packet_present") is False)
    check("record list", isinstance(records, list), "list", isinstance(records, list))
    paths = [item.get("path") for item in records]
    check("sorted unique manifest", paths, sorted(set(paths)), paths == sorted(set(paths)))
    check("manifest count", snapshot.get("candidate_path_count"), len(records), snapshot.get("candidate_path_count") == len(records))
    check("manifest digest", snapshot.get("manifest_sha256"), hashlib.sha256(canonical(records)).hexdigest(), snapshot.get("manifest_sha256") == hashlib.sha256(canonical(records)).hexdigest())
    current_pins = {path: digest(ROOT / path) for path in PINS}
    check("parent hashes", current_pins, PINS, current_pins == PINS)
    authorised: list[str] = []
    complete: list[str] = []
    for item in records:
        path = ROOT / item["path"]
        raw = path.read_bytes()
        _, is_authorised, is_complete = flags(path, raw)
        check(f"byte hash {item['path']}", digest(path), item["sha256"], digest(path) == item["sha256"])
        check(f"authorization bit {item['path']}", is_authorised, item["authorized_marker"], is_authorised == item["authorized_marker"])
        check(f"completion bit {item['path']}", is_complete, item["complete_marker"], is_complete == item["complete_marker"])
        if is_authorised:
            authorised.append(item["path"])
        if is_complete:
            complete.append(item["path"])
    check("no authorized paths", sorted(authorised), [], not authorised and snapshot.get("authorized_paths") == [])
    check("no complete paths", sorted(complete), [], not complete and snapshot.get("complete_paths") == [])
    check("no dynamic fsck field", "fsck" in json.dumps(snapshot).lower(), False, "fsck" not in json.dumps(snapshot).lower())
    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-independent/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-INDEPENDENT-001",
        "status": "PASS_INDEPENDENT_FIXED_OWNER_SNAPSHOT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "source_hashes": current_pins,
        "snapshot_id": snapshot.get("snapshot_id"),
        "candidate_path_count": len(records),
        "authorized_paths": sorted(authorised),
        "complete_paths": sorted(complete),
        "manifest_sha256": snapshot.get("manifest_sha256"),
        "finding": "An independent implementation replays the frozen candidate manifest and parent hashes with no authorized or complete owner marker.",
        "non_claims": snapshot.get("non_claims", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("independent fixed owner snapshot replay mismatch")
    else:
        atomic_write(args.output.resolve(), encoded)
    print(f"PAH-OMC-020 OWNER SNAPSHOT INDEPENDENT: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
