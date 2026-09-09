#!/usr/bin/env python3
"""Integrate the fresh PAH-OMC-020 owner-search snapshot lanes.

The snapshot is a provenance audit.  It does not construct a comparison map,
path law, common Hilbert space, or semigroup.  The verifier reruns the primary,
independent, and hostile readers against one frozen current-byte manifest and
checks that all three retain the same empty authorization/completion sets.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.2.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_snapshot.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py"
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot-v1.2"
)
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def run_lane(script: Path, snapshot: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--snapshot", str(snapshot), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def same_bytes(left: Path, right_payload: dict[str, Any]) -> bool:
    return left.is_file() and left.read_bytes() == (json.dumps(right_payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def compute() -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    saved_paths = {
        "primary": RUN_DIR / "primary.json",
        "independent": RUN_DIR / "independent.json",
        "hostile": RUN_DIR / "hostile.json",
    }
    with tempfile.TemporaryDirectory(prefix="pah020-owner-v12-") as directory:
        folder = Path(directory)
        fresh = {
            "primary": run_lane(PRIMARY, SNAPSHOT, folder / "primary.json"),
            "independent": run_lane(INDEPENDENT, SNAPSHOT, folder / "independent.json"),
            "hostile": run_lane(HOSTILE, SNAPSHOT, folder / "hostile.json"),
        }

    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(name)

    records = snapshot.get("candidate_records", [])
    paths = [record.get("path") for record in records]
    manifest = hashlib.sha256(canonical(records)).hexdigest()
    expected_count = len(records)
    check("snapshot schema", snapshot.get("schema"), "tect/pah-omc020-owner-search-snapshot/1.0", snapshot.get("schema") == "tect/pah-omc020-owner-search-snapshot/1.0")
    check("snapshot status", snapshot.get("status"), "FIXED_SEARCH_SNAPSHOT", snapshot.get("status") == "FIXED_SEARCH_SNAPSHOT")
    check("snapshot id", snapshot.get("snapshot_id"), "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-002", snapshot.get("snapshot_id") == "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-002")
    check("manifest sorted and unique", paths, sorted(set(paths)), paths == sorted(set(paths)))
    check("manifest count", snapshot.get("candidate_path_count"), expected_count, snapshot.get("candidate_path_count") == expected_count)
    check("manifest digest", snapshot.get("manifest_sha256"), manifest, snapshot.get("manifest_sha256") == manifest)
    check("snapshot authorization false", snapshot.get("source_authorized_packet_present"), False, snapshot.get("source_authorized_packet_present") is False)
    check("snapshot authorized set empty", snapshot.get("authorized_paths"), [], snapshot.get("authorized_paths") == [])
    check("snapshot complete set empty", snapshot.get("complete_paths"), [], snapshot.get("complete_paths") == [])

    expected_status = {
        "primary": "PASS_FIXED_OWNER_SNAPSHOT",
        "independent": "PASS_INDEPENDENT_REFRESHED_OWNER_SNAPSHOT",
        "hostile": "PASS_HOSTILE_REFRESHED_OWNER_SNAPSHOT_CONTROLS",
    }
    for name, lane in fresh.items():
        check(f"{name} verdict", lane.get("verdict"), "HOLD_FOR_EVIDENCE", lane.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(f"{name} classification", lane.get("classification"), "auxiliary_support", lane.get("classification") == "auxiliary_support")
        check(f"{name} non-bearing", lane.get("claim_bearing"), False, lane.get("claim_bearing") is False)
        check(f"{name} physical firewall", lane.get("physical_promotion"), False, lane.get("physical_promotion") is False)
        check(f"{name} status", lane.get("status"), expected_status[name], lane.get("status") == expected_status[name])
        if name != "hostile":
            check(f"{name} candidate count", lane.get("candidate_path_count"), expected_count, lane.get("candidate_path_count") == expected_count)
            check(f"{name} manifest", lane.get("manifest_sha256"), manifest, lane.get("manifest_sha256") == manifest)
            check(f"{name} authorized empty", lane.get("authorized_paths"), [], lane.get("authorized_paths") == [])
            check(f"{name} complete empty", lane.get("complete_paths"), [], lane.get("complete_paths") == [])
        check(f"{name} saved replay", saved_paths[name].is_file(), True, same_bytes(saved_paths[name], lane))

    for name in ("independent", "hostile"):
        check(f"{name} snapshot hash", fresh[name].get("snapshot_hash"), digest(SNAPSHOT), fresh[name].get("snapshot_hash") == digest(SNAPSHOT))
    source_hashes = fresh["primary"].get("source_hashes")
    check("parent pins agree", [fresh[name].get("source_hashes") for name in fresh], [source_hashes] * len(fresh), all(fresh[name].get("source_hashes") == source_hashes for name in fresh))

    for label, script in (("independent", INDEPENDENT), ("hostile", HOSTILE)):
        tree = ast.parse(script.read_text(encoding="utf-8"))
        imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        check(f"{label} is non-importing", not any("pah_omc020_owner_packet_snapshot" in item for item in imports), True, not any("pah_omc020_owner_packet_snapshot" in item for item in imports))

    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-v12-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-V12-INTEGRATED-001",
        "task_id": "T-064",
        "status": "PASS_INTEGRATED_CURRENT_OWNER_SNAPSHOT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "lane_counts": {name: len(lane.get("checks", [])) for name, lane in fresh.items()},
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.2.json": digest(SNAPSHOT),
            "verification/scripts/pah_omc020_owner_packet_snapshot.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py": digest(HOSTILE),
        },
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_created_at": snapshot.get("created_at"),
        "candidate_path_count": expected_count,
        "manifest_sha256": manifest,
        "authorized_paths": [],
        "complete_paths": [],
        "finding": "A fresh current-byte scan of the PAH-OMC-020 marker corpus finds 151 candidate files but no source-authorized or complete owner packet. Primary, independent and hostile lanes agree. This is provenance evidence only; no common-space map or process is synthesized.",
        "lean_applicability": "NOT_APPLICABLE_PROVENANCE_HASHING_ONLY",
        "next_single_question": "Can a source owner supply a new versioned packet containing the common H/U_n comparison, anchored N2b liminf/recovery, N2c/N4 boundary escape and exact R-512 minimal-form identification for the unchanged PAH-001 process?",
        "non_claims": [
            "No source-authorized U_n/common-Hilbert map, path law, non-explosion theorem, N2b/N2c/N4/N2d closure or ordered semigroup convergence.",
            "An empty current repository snapshot is not a universal impossibility theorem; an external owner packet requires a new versioned snapshot.",
            "No change to PAH-001 functional, rates, state, carrier, regulator, external Markov time or limit order.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
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
            raise SystemExit("current owner snapshot integrated replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=args.output.name + ".", suffix=".tmp", dir=args.output.parent)
        os.close(descriptor)
        temporary = Path(name)
        try:
            temporary.write_bytes(encoded)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(f"PAH-OMC-020 OWNER SNAPSHOT V1.2 INTEGRATED: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
