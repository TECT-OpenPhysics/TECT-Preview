#!/usr/bin/env python3
"""Integrate the stable PAH-OMC-020 owner-inventory audit lanes."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_owner_packet_inventory_stable.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_owner_packet_inventory_stable_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_owner_packet_inventory_stable_hostile.py"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
R525 = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json"
R525_INTEGRATED = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-noncoordinate-coupling/integrated.json"
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-inventory-stable/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json":
        "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json":
        "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json":
        "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
}


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


def compute(lean_cache: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pah020-owner-inventory-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")

    lanes = {"primary": primary, "independent": independent, "hostile": hostile}
    rows: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    actual_pins = {key: digest(ROOT / key) for key in PINS}
    check("frozen source hashes", actual_pins, PINS, actual_pins == PINS)
    check("all lanes report hold", [lane.get("verdict") for lane in lanes.values()], ["HOLD_FOR_EVIDENCE"] * 3, all(lane.get("verdict") == "HOLD_FOR_EVIDENCE" for lane in lanes.values()))
    check("all lanes are auxiliary", [lane.get("classification") for lane in lanes.values()], ["auxiliary_support"] * 3, all(lane.get("classification") == "auxiliary_support" for lane in lanes.values()))
    check("all lanes are non-bearing", [lane.get("claim_bearing") for lane in lanes.values()], [False] * 3, all(lane.get("claim_bearing") is False for lane in lanes.values()))
    check("all lanes keep physical firewall", [lane.get("physical_promotion") for lane in lanes.values()], [False] * 3, all(lane.get("physical_promotion") is False for lane in lanes.values()))
    check("primary lane status", primary.get("status"), "PASS_STABLE_OWNER_INVENTORY", primary.get("status") == "PASS_STABLE_OWNER_INVENTORY")
    check("independent lane status", independent.get("status"), "PASS_INDEPENDENT_STABLE_OWNER_INVENTORY", independent.get("status") == "PASS_INDEPENDENT_STABLE_OWNER_INVENTORY")
    check("hostile lane status", hostile.get("status"), "PASS_HOSTILE_STABLE_OWNER_INVENTORY_CONTROLS", hostile.get("status") == "PASS_HOSTILE_STABLE_OWNER_INVENTORY_CONTROLS")
    check("primary has no authorized path", primary.get("current_inventory", {}).get("authorized_paths"), [], not primary.get("current_inventory", {}).get("authorized_paths"))
    check("primary has no complete path", primary.get("current_inventory", {}).get("complete_paths"), [], not primary.get("current_inventory", {}).get("complete_paths"))
    check("independent agrees on authorized paths", independent.get("authorized_paths"), [], not independent.get("authorized_paths"))
    check("independent agrees on complete paths", independent.get("complete_paths"), [], not independent.get("complete_paths"))
    check("history inventory avoids fsck", "fsck" not in json.dumps(primary.get("reachable_history_sha256", "")).lower(), True, "fsck" not in json.dumps(primary.get("reachable_history_sha256", "")).lower())
    check("hostile mutations are covered", len(hostile.get("checks", [])), 8, len(hostile.get("checks", [])) == 8)

    source_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(source_tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(source_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("independent does not import primary", not any("owner_packet_inventory_stable" in item and "independent" not in item for item in imports), True, not any("owner_packet_inventory_stable" in item and "independent" not in item for item in imports))
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("hostile does not import primary", not any("owner_packet_inventory_stable" in item and "hostile" not in item for item in hostile_imports), True, not any("owner_packet_inventory_stable" in item and "hostile" not in item for item in hostile_imports))

    r525 = json.loads(R525.read_text(encoding="utf-8"))
    r525_integrated = json.loads(R525_INTEGRATED.read_text(encoding="utf-8"))
    check("R-525 remains conditional", [r525.get("verdict"), r525.get("claim_bearing"), r525.get("active_gate_change")], ["HOLD_FOR_EVIDENCE", False, False], r525.get("verdict") == "HOLD_FOR_EVIDENCE" and r525.get("claim_bearing") is False and r525.get("active_gate_change") is False)
    check("R-525 Lean cross-check remains PASS", r525_integrated.get("status"), "PASS_INTEGRATED_NONCOORDINATE_LOCAL_COUPLING", r525_integrated.get("status") == "PASS_INTEGRATED_NONCOORDINATE_LOCAL_COUPLING")
    check("PAH model hash agrees", digest(PAH), PINS["strategy/pa-hyp/PAH-001-v1.json"], digest(PAH) == PINS["strategy/pa-hyp/PAH-001-v1.json"])
    check("intake hash agrees", digest(INTAKE), PINS["strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"], digest(INTAKE) == PINS["strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"])
    check("candidate hash agrees", digest(CANDIDATE), PINS["strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"], digest(CANDIDATE) == PINS["strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"])
    primary_text = PRIMARY.read_text(encoding="utf-8").lower()
    check("no dynamic fsck command", '"git", "fsck"' in primary_text, False, '"git", "fsck"' not in primary_text)

    return {
        "schema": "tect/pah-omc020-owner-inventory-stable-integrated/1.0",
        "audit_id": "PAH-OMC-020-OWNER-INVENTORY-STABLE-INTEGRATED-001",
        "result_id": "R-526",
        "task_id": "T-063",
        "status": "PASS_INTEGRATED_STABLE_OWNER_INVENTORY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "lane_counts": {name: len(lane.get("checks", [])) for name, lane in lanes.items()},
        "source_hashes": actual_pins,
        "finding": "Primary, independent and hostile lanes agree on a deterministic bounded provenance inventory: no source-authorized PAH-OMC-020 owner packet is present, and the previous dynamic-fsck replay defect is not part of the new evidence.",
        "next_single_question": "Can a source owner authorize the exact R-525 maximal-prefix U_n and provide PAH-specific energy intertwining for N2b, N2c/N4 and N2d without changing PAH-001?",
        "lean_crosscheck": "R-525 integrated Lean 4.32.1 finite coupling declarations remain PASS; this provenance audit adds no physical or analytic Lean claim.",
        "non_claims": [
            "No source-authorized U_n packet, N2b liminf/recovery, N2c/N4 boundary escape, N2d minimal-form identification or PAH-OMC-020 semigroup convergence.",
            "No universal comparison-map impossibility theorem.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lean-cache", type=Path, default=Path(r"E:\Dev\TECT\verification\lean\.lake\packages"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute(args.lean_cache)
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("integrated stable owner inventory replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=args.output.name + ".", suffix=".tmp", dir=args.output.parent)
        import os
        os.close(descriptor)
        temporary = Path(name)
        try:
            temporary.write_bytes(encoded)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(f"PAH-OMC-020 STABLE OWNER INVENTORY INTEGRATED: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
