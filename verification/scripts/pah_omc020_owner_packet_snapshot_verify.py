#!/usr/bin/env python3
"""Integrate the fixed PAH-OMC-020 owner-snapshot verification lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_snapshot.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_packet_snapshot_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_packet_snapshot_hostile.py"
CONTRACT_CHECK = ROOT / "verification/scripts/pah_omc020_n2a_owner_packet_successor_check.py"
SNAPSHOT = ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-snapshot/integrated.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_lane(script: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
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
    with tempfile.TemporaryDirectory(prefix="pah020-owner-snapshot-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        successor = run_lane(CONTRACT_CHECK, folder / "successor.json")

    lanes = {"primary": primary, "independent": independent, "hostile": hostile, "successor": successor}
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(name)

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    check("all lanes hold", [lane.get("verdict") for lane in lanes.values()], ["HOLD_FOR_EVIDENCE"] * 4, all(lane.get("verdict") == "HOLD_FOR_EVIDENCE" for lane in lanes.values()))
    check("all lanes auxiliary", [lane.get("classification") for lane in lanes.values()], ["auxiliary_support"] * 4, all(lane.get("classification") == "auxiliary_support" for lane in lanes.values()))
    check("all lanes non-bearing", [lane.get("claim_bearing") for lane in lanes.values()], [False] * 4, all(lane.get("claim_bearing") is False for lane in lanes.values()))
    check("all lanes physical firewall", [lane.get("physical_promotion") for lane in lanes.values()], [False] * 4, all(lane.get("physical_promotion") is False for lane in lanes.values()))
    check("primary status", primary.get("status"), "PASS_FIXED_OWNER_SNAPSHOT", primary.get("status") == "PASS_FIXED_OWNER_SNAPSHOT")
    check("independent status", independent.get("status"), "PASS_INDEPENDENT_FIXED_OWNER_SNAPSHOT", independent.get("status") == "PASS_INDEPENDENT_FIXED_OWNER_SNAPSHOT")
    check("hostile status", hostile.get("status"), "PASS_HOSTILE_FIXED_OWNER_SNAPSHOT_CONTROLS", hostile.get("status") == "PASS_HOSTILE_FIXED_OWNER_SNAPSHOT_CONTROLS")
    check("successor status", successor.get("status"), "PASS_FIXED_SNAPSHOT_INTAKE", successor.get("status") == "PASS_FIXED_SNAPSHOT_INTAKE")
    check("no authorized paths", primary.get("authorized_paths"), [], primary.get("authorized_paths") == [] and independent.get("authorized_paths") == [] and snapshot.get("authorized_paths") == [])
    check("no complete paths", primary.get("complete_paths"), [], primary.get("complete_paths") == [] and independent.get("complete_paths") == [] and snapshot.get("complete_paths") == [])
    check("fixed manifest agrees", [primary.get("manifest_sha256"), independent.get("manifest_sha256")], [snapshot.get("manifest_sha256")] * 2, primary.get("manifest_sha256") == snapshot.get("manifest_sha256") and independent.get("manifest_sha256") == snapshot.get("manifest_sha256"))
    check("primary and independent candidate counts", [primary.get("candidate_path_count"), independent.get("candidate_path_count")], [snapshot.get("candidate_path_count")] * 2, primary.get("candidate_path_count") == snapshot.get("candidate_path_count") and independent.get("candidate_path_count") == snapshot.get("candidate_path_count"))
    check("snapshot hash agrees with successor", successor.get("source_hashes", {}).get("strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json"), digest(SNAPSHOT), successor.get("source_hashes", {}).get("strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json") == digest(SNAPSHOT))
    check("successor contract hash agrees", successor.get("source_hashes", {}).get("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json"), digest(CONTRACT), successor.get("source_hashes", {}).get("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json") == digest(CONTRACT))
    check("hostile mutations present", len(hostile.get("checks", [])), 10, len(hostile.get("checks", [])) == 10)
    check("successor has nine fields", len(contract.get("required_owner_payload", [])), 9, len(contract.get("required_owner_payload", [])) == 9)
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree) if isinstance(node, ast.Import) for alias in node.names]
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("independent does not import primary", not any("pah_omc020_owner_packet_snapshot" in item and "independent" not in item for item in independent_imports), True, not any("pah_omc020_owner_packet_snapshot" in item and "independent" not in item for item in independent_imports))
    check("hostile does not import primary", not any("pah_omc020_owner_packet_snapshot" in item and "hostile" not in item for item in hostile_imports), True, not any("pah_omc020_owner_packet_snapshot" in item and "hostile" not in item for item in hostile_imports))
    check("no physical promotion in contract", contract.get("provenance", {}).get("physical_promotion"), False, contract.get("provenance", {}).get("physical_promotion") is False)
    check("snapshot contains no fsck field", "fsck" in json.dumps(snapshot).lower(), False, "fsck" not in json.dumps(snapshot).lower())

    return {
        "schema": "tect/pah-omc020-owner-search-snapshot-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-INTEGRATED-001",
        "result_id": "R-528",
        "task_id": "T-063",
        "status": "PASS_INTEGRATED_FIXED_OWNER_SNAPSHOT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "lane_counts": {name: len(lane.get("checks", [])) for name, lane in lanes.items()},
        "source_hashes": {
            "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json": digest(SNAPSHOT),
            "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json": digest(CONTRACT),
            "verification/scripts/pah_omc020_owner_packet_snapshot.py": digest(PRIMARY),
            "codes/foundations/pah_omc020_owner_packet_snapshot_independent.py": digest(INDEPENDENT),
            "codes/foundations/pah_omc020_owner_packet_snapshot_hostile.py": digest(HOSTILE),
            "verification/scripts/pah_omc020_n2a_owner_packet_successor_check.py": digest(CONTRACT_CHECK),
        },
        "finding": "The fixed owner-search snapshot, its independent and hostile lanes, and the N2a successor intake replay exactly with no authorized owner packet. Hash-pinning is now stable against later additions outside the frozen manifest.",
        "lean_applicability": "NOT_APPLICABLE_PROVENANCE_HASHING_ONLY",
        "next_single_question": "Can a source-authorized packet with all nine N2a--N2d fields be supplied, or does the explicit --detect-new scan identify a new candidate requiring a successor snapshot?",
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
            raise SystemExit("integrated fixed owner snapshot replay mismatch")
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
    print(f"PAH-OMC-020 OWNER SNAPSHOT INTEGRATED: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
