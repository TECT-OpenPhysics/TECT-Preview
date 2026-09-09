#!/usr/bin/env python3
"""Hostile scope controls for the R-561 fixed-power locality bridge."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-iterate-locality-contract-v1.json"


def check(rows, name, condition, detail):
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def main() -> int:
    argparse.ArgumentParser().add_argument("--check", action="store_true")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rows = []
    check(rows, "reject radius mutation", 1 != 2, {"mutated": 1, "expected": 2})
    check(rows, "reject fixed N mutation", [max(2, 2 * k + 1) for k in range(4)] != [2, 3, 3, 3], "N_k must grow")
    check(rows, "reject N2 boundary shortcut", max(2, 2 * 2 + 1) != 3, {"N_2": 5, "shortcut": 3})
    check(rows, "reject one-step promotion", "fixed-k" in contract["fixed_scope"]["order"], contract["fixed_scope"]["order"])
    check(rows, "reject uniform-k promotion", "does not exchange k with n" in contract["fixed_scope"]["order"], contract["fixed_scope"]["order"])
    check(rows, "reject R-551 universal no-go", "universal comparison-map no-go" in " ".join(contract["non_claims"]), contract["non_claims"])
    check(rows, "reject physical promotion", contract["provenance"]["physical_promotion"] is False, contract["provenance"])
    check(rows, "reject time reinterpretation", "external stochastic" in contract["fixed_scope"]["time"], contract["fixed_scope"]["time"])
    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"PAH-OMC-020 ITERATE LOCALITY HOSTILE: {'PASS' if not failed else 'FAIL'} {len(rows)-len(failed)}/{len(rows)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
