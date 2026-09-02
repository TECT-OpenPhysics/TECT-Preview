#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-001 lumpability boundary diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-r480-pah-lumpability-boundary"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    primary = load(args.directory / "lumpability.json")
    independent = load(args.directory / "independent.json")
    expected_parent = (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    expected_contract = (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )
    assert primary["source_authorities"][0]["sha256"] == expected_parent
    assert primary["source_authorities"][1]["sha256"] == expected_contract
    assert independent["source_hashes"]["PAH-001"] == expected_parent
    assert independent["source_hashes"]["PAH-OMC-001"] == expected_contract
    assert primary["audit_id"] == independent["audit_id"] == "PAH-OMC-LUMP-AUDIT-001"
    assert primary["exploration_id"] == independent["exploration_id"] == "EXP-001362"
    assert primary["verdict"] == independent["verdict"] == "ROUTE_LOCAL_STRONG_LUMPABILITY_FAIL"
    assert primary["stage2_status"] == independent["stage2_status"] == "HOLD_FOR_EVIDENCE"
    assert primary["assertions"]["cases"] == independent["assertions"]["cases"]
    assert primary["assertions"]["all_pass"] and independent["assertions"]["all_pass"]
    print(
        "PAH-OMC-LUMP-AUDIT-001 INTEGRATED PASS "
        f"primary={primary['assertions']['cases']} "
        f"independent={independent['assertions']['cases']} "
        f"verdict={primary['verdict']}"
    )


if __name__ == "__main__":
    main()
