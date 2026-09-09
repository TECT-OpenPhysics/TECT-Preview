#!/usr/bin/env python3
"""Integrate the refreshed PAH-OMC-020 owner-search lanes."""

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
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_snapshot.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot-v1.1/integrated.json"
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


def run_lane(script: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--snapshot", str(SNAPSHOT), "--output", str(output)],
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


def compute() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pah020-owner-v11-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    lanes = {"primary": primary, "independent": independent, "hostile": hostile}
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(name)

    check("all lanes hold", [lane.get("verdict") for lane in lanes.values()], ["HOLD_FOR_EVIDENCE"] * 3, all(lane.get("verdict") == "HOLD_FOR_EVIDENCE" for lane in lanes.values()))
    check("all lanes auxiliary", [lane.get("classification") for lane in lanes.values()], ["auxiliary_support"] * 3, all(lane.get("classification") == "auxiliary_support" for lane in lanes.values()))
    check("all lanes non-bearing", [lane.get("claim_bearing") for lane in lanes.values()], [False] * 3, all(lane.get("claim_bearing") is False for lane in lanes.values()))
    check("physical firewall", [lane.get("physical_promotion") for lane in lanes.values()], [False] * 3, all(lane.get("physical_promotion") is False for lane in lanes.values()))
    check("primary status", primary.get("status"), "PASS_FIXED_OWNER_SNAPSHOT", primary.get("status") == "PASS_FIXED_OWNER_SNAPSHOT")
    check("independent status", independent.get("status"), "PASS_INDEPENDENT_REFRESHED_OWNER_SNAPSHOT", independent.get("status") == "PASS_INDEPENDENT_REFRESHED_OWNER_SNAPSHOT")
    check("hostile status", hostile.get("status"), "PASS_HOSTILE_REFRESHED_OWNER_SNAPSHOT_CONTROLS", hostile.get("status") == "PASS_HOSTILE_REFRESHED_OWNER_SNAPSHOT_CONTROLS")
    check("no authorized paths", [snapshot.get("authorized_paths"), primary.get("authorized_paths"), independent.get("authorized_paths")], [[], [], []], snapshot.get("authorized_paths") == primary.get("authorized_paths") == independent.get("authorized_paths") == [])
    check("no complete paths", [snapshot.get("complete_paths"), primary.get("complete_paths"), independent.get("complete_paths")], [[], [], []], snapshot.get("complete_paths") == primary.get("complete_paths") == independent.get("complete_paths") == [])
    expected_manifest = snapshot.get("manifest_sha256")
    check("manifest agrees", [primary.get("manifest_sha256"), independent.get("manifest_sha256")], [expected_manifest, expected_manifest], primary.get("manifest_sha256") == independent.get("manifest_sha256") == expected_manifest)
    expected_count = snapshot.get("candidate_path_count")
    check("candidate count agrees", [primary.get("candidate_path_count"), independent.get("candidate_path_count")], [expected_count, expected_count], primary.get("candidate_path_count") == independent.get("candidate_path_count") == expected_count)
    check("refreshed snapshot hash agrees", [independent.get("snapshot_hash"), hostile.get("snapshot_hash")], [digest(SNAPSHOT)] * 2, independent.get("snapshot_hash") == hostile.get("snapshot_hash") == digest(SNAPSHOT))
    check("primary manifest agrees", primary.get("manifest_sha256"), expected_manifest, primary.get("manifest_sha256") == expected_manifest)
    check("parent pins agree", primary.get("source_hashes"), PINS, primary.get("source_hashes") == PINS and independent.get("source_hashes") == PINS and hostile.get("source_hashes") == PINS)
    check("hostile mutations present", len(hostile.get("checks", [])), 10, len(hostile.get("checks", [])) == 10)

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree) if isinstance(node, ast.Import) for alias in node.names]
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("independent is non-importing", not any("pah_omc020_owner_snapshot_v11" in item for item in independent_imports), True, not any("pah_omc020_owner_snapshot_v11" in item for item in independent_imports))
    check("hostile is non-importing", not any("pah_omc020_owner_snapshot_v11" in item for item in hostile_imports), True, not any("pah_omc020_owner_snapshot_v11" in item for item in hostile_imports))
    check("snapshot schema", snapshot.get("schema"), "tect/pah-omc020-owner-search-snapshot/1.0", snapshot.get("schema") == "tect/pah-omc020-owner-search-snapshot/1.0")
    check("snapshot timestamp", snapshot.get("created_at"), "2026-09-08T00:00:00Z", snapshot.get("created_at") == "2026-09-08T00:00:00Z")
    check("no physical non-claim", snapshot.get("non_claims", [])[-1].startswith("No physical"), True, snapshot.get("non_claims", [])[-1].startswith("No physical"))

    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-v11-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-V11-INTEGRATED-001",
        "task_id": "T-075",
        "status": "PASS_INTEGRATED_REFRESHED_OWNER_SNAPSHOT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "lane_counts": {name: len(lane.get("checks", [])) for name, lane in lanes.items()},
        "source_hashes": {
            **PINS,
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.1.json": digest(SNAPSHOT),
            "verification/scripts/pah_omc020_owner_packet_snapshot.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_owner_snapshot_v11_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py": digest(HOSTILE),
        },
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_created_at": snapshot.get("created_at"),
        "candidate_path_count": expected_count,
        "manifest_sha256": expected_manifest,
        "authorized_paths": [],
        "complete_paths": [],
        "finding": "The refreshed 101-file snapshot replays with independent and hostile checks; all owner-authorization and completion sets remain empty. The old snapshot's changed temporal-work hash is treated as provenance drift, not as a source packet.",
        "lean_applicability": "NOT_APPLICABLE_PROVENANCE_HASHING_ONLY",
        "next_single_question": "Can a source owner supply a versioned packet containing the stopped path law, filtration, compensator and exact eta-to-hitting-event attribution for the unchanged PAH-001 process?",
        "non_claims": [
            "No source-authorized path law, non-explosion theorem, N2b/N2c/N4/N2d closure or ordered semigroup convergence.",
            "No universal impossibility theorem follows from an empty repository snapshot; external candidates require a new versioned snapshot.",
            "No change to PAH-001 functional, rates, state, carrier, regulator, Markov time or limit order.",
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
            raise SystemExit("refreshed owner snapshot integrated replay mismatch")
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
    print(f"PAH-OMC-020 OWNER SNAPSHOT V1.1 INTEGRATED: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
