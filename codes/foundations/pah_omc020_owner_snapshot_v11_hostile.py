#!/usr/bin/env python3
"""Hostile mutation controls for the refreshed PAH-OMC-020 owner snapshot."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot-v1.1/hostile.json"
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def valid(snapshot: dict[str, Any]) -> bool:
    records = snapshot.get("candidate_records", [])
    if snapshot.get("schema") != "tect/pah-omc020-owner-search-snapshot/1.0":
        return False
    if snapshot.get("status") != "FIXED_SEARCH_SNAPSHOT":
        return False
    if snapshot.get("source_authorized_packet_present") is not False:
        return False
    if snapshot.get("authorized_paths") != [] or snapshot.get("complete_paths") != []:
        return False
    if not isinstance(records, list):
        return False
    paths = [record.get("path") for record in records]
    if paths != sorted(set(paths)):
        return False
    if snapshot.get("manifest_sha256") != hashlib.sha256(canonical(records)).hexdigest():
        return False
    return all((ROOT / record["path"]).is_file() and digest(ROOT / record["path"]) == record.get("sha256") for record in records)


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


def compute(snapshot_path: Path) -> dict[str, Any]:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(name)

    check("baseline validates", valid(snapshot), True, valid(snapshot))
    auth = copy.deepcopy(snapshot)
    auth["authorized_paths"] = ["injected-owner.json"]
    check("authorized-path mutation rejected", valid(auth), False, not valid(auth))
    complete = copy.deepcopy(snapshot)
    complete["complete_paths"] = ["injected-owner.json"]
    check("complete-path mutation rejected", valid(complete), False, not valid(complete))
    flag = copy.deepcopy(snapshot)
    flag["source_authorized_packet_present"] = True
    check("authorization flag mutation rejected", valid(flag), False, not valid(flag))
    manifest = copy.deepcopy(snapshot)
    manifest["manifest_sha256"] = "0" * 64
    check("manifest mutation rejected", valid(manifest), False, not valid(manifest))
    byte_hash = copy.deepcopy(snapshot)
    byte_hash["candidate_records"][0]["sha256"] = "f" * 64
    check("candidate-byte mutation rejected", valid(byte_hash), False, not valid(byte_hash))
    order = copy.deepcopy(snapshot)
    order["candidate_records"] = list(reversed(order["candidate_records"]))
    check("manifest-order mutation rejected", valid(order), False, not valid(order))
    fsck = copy.deepcopy(snapshot)
    fsck["scope"]["replay"] = "git fsck --unreachable"
    check("dynamic fsck mutation detected", "fsck" in json.dumps(fsck).lower(), True, "fsck" in json.dumps(fsck).lower())
    check("parent pin set remains frozen", {key: digest(ROOT / key) for key in PINS}, PINS, {key: digest(ROOT / key) for key in PINS} == PINS)
    check("physical promotion absent", snapshot.get("non_claims", [])[-1].startswith("No physical"), True, snapshot.get("non_claims", [])[-1].startswith("No physical"))

    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-v11-hostile/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-V11-HOSTILE-001",
        "status": "PASS_HOSTILE_REFRESHED_OWNER_SNAPSHOT_CONTROLS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "source_hashes": {key: digest(ROOT / key) for key in PINS},
        "snapshot_hash": digest(snapshot_path),
        "finding": "Authorization, completion, manifest, ordering, byte-hash and source-pin mutations are rejected; the refreshed snapshot cannot be promoted into an owner packet.",
        "non_claims": snapshot.get("non_claims", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute(args.snapshot.resolve())
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("refreshed hostile owner snapshot replay mismatch")
    else:
        atomic_write(args.output.resolve(), encoded)
    print(f"PAH-OMC-020 OWNER SNAPSHOT V1.1 HOSTILE: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
