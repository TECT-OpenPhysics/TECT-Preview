#!/usr/bin/env python3
"""Non-importing PAH-OMC-030 source and obligation audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-030-prereg-v1.json"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc030-bridge/independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    contract = json.loads(PREREG.read_text(encoding="utf-8"))
    pin_failures = []
    for rel, expected in contract["source_files"].items():
        actual = digest(ROOT / rel)
        if actual != expected:
            pin_failures.append(rel)
    checks = {
        "all_source_pins": not pin_failures,
        "fixed_n_before_anchored_n": contract["exact_scope"]["order"].startswith("First j->infinity at fixed n"),
        "terminal_square_is_frozen": "unsplit" in contract["exact_scope"]["boundary"] and "terminal" in contract["exact_scope"]["boundary"],
        "same_D_is_frozen": contract["exact_scope"]["domain"].startswith("D is exactly the R-511"),
        "r514_bridge_is_fixed_n": "fixed-n" in (ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json").read_text(encoding="utf-8"),
        "r568_does_not_claim_finite_convergence": "No original finite-semigroup convergence" in (ROOT / "strategy/pa-hyp/PAH-OMC-029-result-v1.json").read_text(encoding="utf-8"),
        "N2a_is_unproved": "U_n" in contract["required_bridges"]["N2a"],
        "N2b_is_unproved": "liminf" in contract["required_bridges"]["N2b"],
        "N2c_is_unproved": "boundary" in contract["required_bridges"]["N2c_N4"],
        "N2d_is_unproved": "minimal" in contract["required_bridges"]["N2d"]
    }
    payload = {
        "schema": "tect/pah-omc030-independent/1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "checks": checks,
        "pin_failures": pin_failures,
        "coverage": "Independent source/contract reconstruction; no import of pah_omc030_verify.py and no claim that the missing bridges hold.",
        "non_claims": ["No finite-to-target convergence", "No physical Pre-A/QFT/gravity/continuum/Yang-Mills/mass-gap/TOE conclusion"]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PAH-OMC-030 INDEPENDENT: {payload['status']}; verdict=HOLD_FOR_EVIDENCE")
    return 0 if args.check and payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
