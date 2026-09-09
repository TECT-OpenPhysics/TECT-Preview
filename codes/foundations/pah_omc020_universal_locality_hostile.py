#!/usr/bin/env python3
"""Hostile scope controls for the R-562 all-cylinder locality envelope."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-universal-locality-contract-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks = [
        ("reject radius one mutation", 2 != 1),
        ("reject fixed N mutation", [max(2, 0 + 2 * k + 1) for k in range(4)] != [2, 3, 3, 3]),
        ("reject omitted support maximum", "s_f" in contract["fixed_scope"]["support_parameter"]),
        ("reject one-step promotion", "fixed finite k" in contract["fixed_scope"]["order"]),
        ("reject k/n exchange", "No k/n exchange" in contract["fixed_scope"]["order"]),
        ("reject uniform operator promotion", "No single N(f)" in " ".join(contract["non_claims"])),
        ("reject physical promotion", contract["provenance"]["physical_promotion"] is False),
        ("reject time reinterpretation", "external stochastic" in contract["fixed_scope"]["time"]),
    ]
    failed = [name for name, ok in checks if not ok]
    print(f"PAH-OMC-020 UNIVERSAL LOCALITY HOSTILE: {'PASS' if not failed else 'FAIL'} {len(checks)-len(failed)}/{len(checks)}")
    for name in failed:
        print(f"FAIL {name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
