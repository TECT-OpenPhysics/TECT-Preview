#!/usr/bin/env python3
"""Hostile scope controls for the R-563 route-local obstruction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-diagonal-locality-contract-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks = [
        ("reject radius-one mutation", "r=2" in contract["fixed_scope"]["radius"]),
        ("reject finite-table-as-uniform", "fixed finite n" in contract["exact_statement"] and "every k" in contract["exact_statement"]),
        ("reject k/n exchange", "No exponential series" in contract["fixed_scope"]["order"]),
        ("reject full semigroup no-go", "not a no-go" in " ".join(contract["non_claims"])),
        ("reject uniform-tail promotion", "uniform-in-k" in " ".join(contract["missing_assumptions"])),
        ("reject changed dynamics", "no functional, rate, state" in contract["fixed_scope"]["model"]),
        ("reject physical promotion", contract["provenance"]["physical_promotion"] is False),
        ("reject time reinterpretation", "external stochastic" in contract["fixed_scope"]["time"]),
    ]
    failed = [name for name, ok in checks if not ok]
    print(f"PAH-OMC-020 DIAGONAL LOCALITY HOSTILE: {'PASS' if not failed else 'FAIL'} {len(checks)-len(failed)}/{len(checks)}")
    for name in failed:
        print(f"FAIL {name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
